# coding=utf8
""" Brain Service

Handles all Authorization / Login requests
"""

__author__		= "Chris Nasr"
__copyright__	= "Ouroboros Coding Inc."
__email__		= "chris@ouroboroscoding.com"
__created__		= "2022-08-26"

# Ouroboros imports
from body import create, Error, regex, Response, ResponseException, Service
from config import config
from jobject import jobject
import memory
from nredis import nr
from rest_mysql.Record_MySQL import DuplicateException
from strings import random
from tools import combine, evaluate, get_client_ip
import undefined

# Python imports
import requests
from typing import List
import uuid

# Pip imports
from googleapiclient.discovery import build as gapi_build
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

# Records imports
from brain.records import cache as record_cache, Key, Permissions, User

# Local
from brain import errors
from brain.helpers import access, users

class Brain(Service):
	"""Brain Service class

	Service for authorization, sign in, sign up, permissions etc.
	"""

	def __init__(self, google_flow):
		"""Constructor

		Initialises the instance

		Arguments:
			google_flow (google_auth_oauthlib.flow): The google auth flow

		Returns:
			Brain
		"""

		# Store the google flow
		self._google_flow = google_flow

		# Init the config
		self.reset()

	def _create_key(self, user, type_):
		"""Create Key

		Creates a key used for verification of the user

		Arguments:
			user (str): The ID of the user
			type_ (str): The type of key to make

		Returns:
			str
		"""

		# Create an instance
		oKey = Key({
			'_id': random(32, ['0x']),
			'user': user,
			'type': type_
		})

		# Loop until we resolve the issue
		while True:
			try:

				# Create the key record
				oKey.create()

				# Return the key
				return oKey['_id']

			# If we got a duplicate key error
			except DuplicateException as e:

				# If the primary key is the duplicate
				if 'PRIMARY' in e.args[1]:

					# Generate a new key and try again
					oKey['_id'] = random(32, ['0x'])
					continue

				# Else, the type has already been used for the user
				else:

					# Find and return the existing key
					return Key.filter({
						'user': user,
						'type': type_
					}, raw = [ '_id' ], limit = 1)['_id']

	def _recaptcha_v2(self, response: str, ip: str) -> dict:
		"""ReCaptcha V2

		Verifies a google recaptcha v2 response

		Arguments:
			response (str): The response delivered by the UI
			ip (str): The IP of the client that generated the response

		Returns:
			dict
		"""

		# If the secret is missing
		if 'secret' not in self._conf['recaptcha']:
			raise ResponseException(error = (
				errors.BAD_CONFIG, [ 'recaptcha.secret', 'missing ']
			))

		# Generate the URL
		sURL = 'https://www.google.com/recaptcha/api/siteverify' \
				'?secret=%s' \
				'&response=%s' \
				'&remoteip=%s' % (
			self._conf['recaptcha']['secret'],
			response,
			ip
		)

		# Run the request
		oResponse = requests.get(sURL)

		# Return the result
		return oResponse.json()

	def _recaptcha_v3(self, token: str, action: str) -> dict:
		"""ReCaptcha Assessment

		ReCaptcha V3, create an assessment to analyze the risk of a UI action

		Arguments:
			token: The generated token obtained from the client
			action: Action name corresponding to the token

		Returns:
			dict
		"""

		# Check the minimum config
		try:
			evaluate(
				self._conf['recaptcha'],
				[ 'api_key', 'key', 'project' ]
			)
		except ValueError as e:
			return ResponseException(error = (
				errors.BAD_CONFIG,
				[ [ 'recaptcha.%s' % f, 'missing' ] for f in e.args ]
			))

		# Generate the URL and JSON body
		sURL = 'https://recaptchaenterprise.googleapis.com' \
				'/v1/projects/%s/assessments?key=%s' % (
			self._conf['recaptcha']['project'],
			self._conf['recaptcha']['api_key']
		)

		# Run the request using the API
		oResponse = requests.post(sURL, json = {
			'event': {
				'token': token,
				'expectedAction': action,
				'siteKey': self._conf['recaptcha']['key']
			}
		})

		# Pull out the data
		dData = oResponse.json()

		# If the token is not valid
		if not dData['tokenProperties']['valid']:
			return {
				'result': False,
				'reason': dData['tokenProperties']['invalidReason']
			}

		# Check if the expected action was executed.
		if dData['tokenProperties']['action'] != action:
			return {
				'result': False,
				'reason': 'invalid action'
			}

		# If the score is below 0.2, deny it
		elif dData['riskAnalysis']['score'] < 0.2:
			return {
				'result': False,
				'reason': [ 'high risk user', dData['riskAnalysis']['reasons'] ]
			}

		# Else, return ok
		return { 'result': True }

	@classmethod
	def _internal_or_verify(cls,
		req: jobject,
		name: str,
		right: int,
		id: str = undefined
	) -> access.INTERNAL | access.VERIFY:
		"""Internal or Verify

		Does the same thing as the access method of the same name, but without \
		the round trip of talking to ourself

		Arguments:
			request (request): The bottle request for the headers
			session (memory._Memory): The session object to check
			name (str | str[]): The name(s) of the permission to check
			right (uint | uint[]): The right(s) to check for
			id (str): Optional ID to check against

		Raises:
			body.ResponseException

		Returns:
			access.INTERNAL | access.VERIFY
		"""

		# If we have an internal key
		if 'Authorize-Internal' in req.request.headers:

			print(req.request.headers['Authorize-Internal'])

			# Run the internal check
			access.internal()

			# Return that the request passed the internal check
			return access.INTERNAL

		# Else
		else:

			# Make sure the user has the proper permission to do this
			cls._verify(
				(req.session.user._id, req.session.portal),
				name,
				right,
				id
			)

			# Return that the request passed the verify check
			return access.VERIFY

	@classmethod
	def _verify(cls,
		_id: tuple,
		name: str | List[str],
		right: int | List[int],
		id: str = undefined
	) -> bool:
		"""Verify

		Checks the user currently in the session has access to the requested \
		permission

		Arguments:
			_id (tuple): The user ID and portal of the permissions
			name (str | str[]): The name(s) of the permission to check
			right (uint | uint[]): The specific right(s) on the permission to \
				verify
			id (str): Optional ID to check against

		Returns:
			bool
		"""

		# Find the permissions
		dPermissions = Permissions.get(_id, raw = True)

		# If there's no such permissions
		if not dPermissions:
			raise ResponseException(
				error = (errors.BAD_PORTAL, _id[1])
			)

		# If one permission was requested
		if isinstance(name, str):

			# If we don't have it
			if name not in dPermissions['rights']:
				return False

			# Set the name to use
			sName = name

		# Else, if it's a list
		elif isinstance(name, list):

			# Go through each one, if one matches, store it
			for s in name:
				if s in dPermissions['rights']:
					sName = s
					break

			# Else, return failure
			else:
				return False

		# Else, invalid name data
		else:
			raise ResponseException(error=(
				errors.body.DATA_FIELDS,
				[ [ 'name', 'invalid, must be string or string[]' ] ]
			))

		# If no ID was passed
		if id is undefined:

			# If the user has the all rights
			if access.RIGHTS_ALL_ID in dPermissions['rights'][sName]:
				sID = access.RIGHTS_ALL_ID

			# Else, no rights
			else:
				return False

		# Else, an ID was passed
		else:

			# If the user has the ID on the right
			if id in dPermissions['rights'][sName]:
				sID = id

			# Else, if the user has the all
			elif access.RIGHTS_ALL_ID in dPermissions['rights'][sName]:
				sID = access.RIGHTS_ALL_ID

			# Else, no rights
			else:
				return False

		# If one right was requested
		if isinstance(right, int):

			# If the permission doesn't contain the requested right
			if not dPermissions['rights'][sName][sID] & right:
				return False

		# Else, if it's a list of rights
		elif isinstance(right, list):

			# Go through each one, if it passes, break
			for i in right:
				if dPermissions['rights'][sName][sID] & i:
					break

			# Else, no rights matched
			else:
				return False

		# Else, invalid right data
		else:
			raise ResponseException(error=(
				errors.body.DATA_FIELDS,
				[ [ 'right', 'invalid, must be int or int[]' ] ]
			))

		# Seems ok
		return True

	def google_auth_create(self, req: jobject) -> Response:
		"""Google Auth create

		Handles converting the response from Google into an email and then \
		either creating the account for the user or signing them in

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try:
			evaluate(req.data, [ 'redirect', 'url' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS,
				[ [ f, 'missing' ] for f in e.args ]
			)

		# Make sure the URL has the {key} field
		if '{key}' not in req.data['url']:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'url', 'missing "{key}"' ] ]
			)

		# If the portal was not passed
		if 'portal' not in req.data:
			req.data['portal'] = ''

		# Pass the requested URL to the flow so google can confirm
		try:
			self._google_flow.fetch_token(
				authorization_response = req.data['redirect']
			)
		except InvalidGrantError as e:
			return Error(errors.BAD_OAUTH, e.args)

		# Use the credentials to fetch the user's info
		UserInfoService = gapi_build(
			'oauth2',
			'v2',
			credentials = self._google_flow.credentials
		)
		dInfo = UserInfoService.userinfo().get().execute()

		# Look for the user
		dUser = User.filter({
			'email': dInfo['email']
		}, raw = [ '_id' ], limit = 1)

		# If the user exists
		if dUser:

			# Check if the user has permissions in the given portal
			dPerms = Permissions.get(
				( dUser['_id'], req.data['portal'] ),
				raw = [ 'user' ]
			)

			# If we don't have permissions for the given portal
			if not dPerms:
				return Error(errors.BAD_PORTAL, req.data['portal'])

			# Set user ID
			sID = dUser['_id']

		# Else, no such user
		else:

			# Do we have a locale convert table, and is the locale in it?
			if 'locales' in self._conf['google'] and \
				dInfo['locale'] in self._conf['google']['locales']:

				# Use the table to get an acceptable locale
				sLocale = self._conf['google']['locales'][dInfo['locale']]
			else:

				# Just use the default locale
				sLocale = self._conf['user_default_locale']

			# Validate by creating a Record instance
			try:
				oUser = User({
					'email': dInfo['email'],
					'passwd': users.EMPTY_PASS,
					'locale': sLocale,
					'first_name': dInfo['given_name'],
					'last_name': dInfo['family_name'],
					'verified': dInfo['verified_email']
				})
			except ValueError as e:
				return Error(errors.body.DATA_FIELDS, e.args[0])

			# Create the record
			sID = oUser.create(changes = { 'user': users.SYSTEM_USER_ID })
			if not sID:
				return Error(errors.body.DB_CREATE_FAILED, 'user')

			# Add portal permission
			oPermissions = Permissions({
				'user': sID,
				'portal': req.data['portal'],
				'rights': {}
			})
			if not oPermissions.create(
				changes = { 'user': users.SYSTEM_USER_ID }
			):
				return Error(errors.body.DB_CREATE_FAILED, 'permissions')

			# If the email is not verified
			if not oUser['verified']:

				# Create key for setup validation
				sSetupKey = self._create_key(sID, 'setup')

				# Email the user the setup link
				oResponse = create('mouth', 'email', { 'data': {
					'template': {
						'name': 'setup_user',
						'locale': sLocale,
						'portal': req.data['portal'],
						'variables': {
							'key': sSetupKey,
							'url': req.data['url'].replace(
								'{key}',
								sSetupKey
							)
						},
					},
					'to': req.data['email']
				}}, access.generate_key())
				if oResponse.error:
					Key.delete_get(sSetupKey)
					return oResponse

		# Create a new session
		oSesh = memory.create('sesh:%s' % uuid.uuid4().hex)

		# Store the user ID and portal in th session
		oSesh['user'] = { '_id': sID }
		oSesh['portal'] = req.data['portal']

		# Save the session
		oSesh.save()

		# Return the session ID, primary user data, and portal name
		return Response({
			'session': oSesh.key(),
			'user': oSesh['user'],
			'portal': oSesh['portal']
		})

	def passwd_verify_create(self, req: jobject) -> Response:
		"""Password Verify create

		Takes a password and verifies if it matches the currently signed in \
		user's password. Requires session

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# If the password was not sent
		if 'passwd' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ 'passwd', 'missing' ]
			)

		# Get the user associated with the session
		oUser = User.get(req.session.user._id)
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD,
				[ req.session.user._id, 'user' ]
			)

		# Check the password and return the result
		return Response(
			oUser.password_validate(req.data['passwd'])
		)

	def permissions_read(self, req: jobject) -> Response:
		"""Permissions read

		Returns all permissions associated with a user

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# If the user is missing
		if 'user' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'user', 'missing' ] ]
			)

		# Check internal or verify
		self._internal_or_verify(req, 'brain_permission', access.UPDATE)

		# Fetch the Permissions
		dPermissions = Permissions.filter({
			'user': req.data['user']
		}, raw=True)

		# Return all permissions
		return Response(dPermissions)

	def permissions_update(self, req: jobject) -> Response:
		"""Permissions update

		Updates the permissions for a single user

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try:
			evaluate(req.data, [ 'user', 'rights' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS,
				[ [ f, 'missing' ] for f in e.args ]
			)

		# If the portal wasn't passed
		if 'portal' not in req.data:
			req.data['portal'] = ''

		# Check internal or verify
		iWhich = self._internal_or_verify(
			req, 'brain_permission', access.UPDATE
		)

		# Set the session user based on the mode of access
		sSessionUser = iWhich == access.INTERNAL and \
						users.SYSTEM_USER_ID or \
						req.session.user._id

		# If the user doesn't exist
		if not User.exists(req.data['user']):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['user'], 'user' ]
			)

		# Find the permissions
		oPermissions = Permissions.get(
			(req.data['user'], req.data['portal'])
		)

		# If they don't exist
		if not oPermissions:

			# If the user doesn't exist
			if not User.exists(req.data['user']):
				return Error(
					errors.body.DB_NO_RECORD,
					[ req.data['user'], 'user' ]
				)

			# Test the new record
			try:
				oPermissions = Permissions({
					'user': req.data['user'],
					'portal': req.data['portal'],
					'rights': req.data['rights']
				})
			except ValueError as e:
				return Error(errors.body.DATA_FIELDS, e.args[0])

			# Create the record
			bRes = oPermissions.create(changes = { 'user': sSessionUser })

		# Else, we are updating
		else:

			# Try to set the new permissions
			try:

				# If a merge was requested
				if 'merge' in req.data and req.data['merge']:

					# Generate the new merged permissions
					dPerms = combine(
						oPermissions['rights'],
						req.data['rights']
					)

					# Go through each right looking for 0 (zero), if it's found,
					#	remove the right altogether. This allows us to "remove"
					#	rights via a merge
					for a in list(dPerms.keys()):
						for b in list(dPerms[a].keys()):
							if dPerms[a][b] == 0:
								del dPerms[a][b]
						if not dPerms[a]:
							del dPerms[a]

					# If we have no more permissions
					if not dPerms:

						# Delete the permissions
						bRes = oPermissions.delete(
							changes = { 'user': sSessionUser }
						)

						# Clear the cache
						if bRes:
							Permissions.clear(
								(req.data['user'], req.data['portal'])
							)

						# Return the result
						return Response(bRes)

					# Set the new merged permissions
					oPermissions['rights'] = dPerms

				# Else, overwrite the rights with the new ones
				else:
					oPermissions['rights'] = req.data['rights']

			# If the rights are bad
			except ValueError as e:
				return Error(errors.body.DATA_FIELDS, [ e.args[0] ])

			# Save the permissions
			bRes = oPermissions.save(changes = { 'user': sSessionUser })

			# Clear the cache
			if bRes:
				Permissions.clear(
					(req.data['user'], req.data['portal'])
				)

		# Return the result
		return Response(bRes)

	def permissions_add_create(self, req: jobject) -> Response:
		"""Permissions Add create

		Addes a specific permission type to existing permissions

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ 'user', 'rights' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ])

		# If the portal wasn't passed
		if 'portal' not in req.data:
			req.data['portal'] = ''

		# Check internal or verify
		iWhich = self._internal_or_verify(
			req, 'brain_permission', access.UPDATE
		)

		# Set the session user based on the mode of access
		sSessionUser = iWhich == access.INTERNAL and \
						users.SYSTEM_USER_ID or \
						req.session.user._id

		# If the user doesn't exist
		if not User.exists(req.data['user']):
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['user'], 'user' ]
			)

		# Find the permissions
		oPermissions = Permissions.get(
			(req.data['user'], req.data['portal'])
		)
		if not oPermissions:
			return Error(
				errors.body.DB_NO_RECORD,
				[ req.data['user'], req.data['portal'], 'permissions' ]
			)

		# Combine the rights
		dRights = combine(oPermissions['rights'], req.data['rights'])

		# Try to update the permissions
		try:
			oPermissions['rights'] = dRights
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, [ e.args[0] ])

		# Save and return the results
		return Response(
			oPermissions.save(changes={'user': sSessionUser})
		)

	def reset(self):
		"""Reset

		Called to reset the config and connections

		Returns:
			Brain
		"""

		# Get config
		self._conf = config.brain({
			'internal': {
				'salt': ''
			},
			'portals': {
				'': {
					'ttl': 86400,
					'rights': {}
				}
			},
			'redis': 'session',
			'recaptcha': {
				'version': 'v3'
			},
			'user_default_locale': 'en-US'
		})

		# Go through each portal and make sure we have a TTL
		for p in self._conf['portals']:
			if 'rights' not in self._conf['portals'][p]:
				self._conf['portals'][p]['rights'] = { }
			if 'ttl' not in self._conf['portals'][p]:
				self._conf['portals'][p]['ttl'] = 0

		# If the salt is set and invalid
		if self._conf['internal']['salt'] and \
			len(self._conf['internal']['salt']) % 16 != 0:

			# Raise an error with an explanation
			raise ValueError(
				'brain.internal.salt',
				'must be a string with a length that is multiples of 16 ' \
					'characters'
			)

		# Create a connection to Redis
		self._redis = nr(self._conf['redis'])

		# Pass the Redis connection to the records
		record_cache(self._redis)

		# Return self for chaining
		return self

	def search_read(self, req: jobject) -> Response:
		"""Search

		Looks up users by search / query

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check permissions
		self._verify(
			(req.session.user._id, req.session['portal']),
			'brain_user',
			access.READ
		)

		# Check for filter
		if 'filter' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'filter', 'missing' ] ]
			)

		# If the filter isn't a dict
		if not isinstance(req.data['filter'], dict):
			return Error(
				errors.body.DATA_FIELDS, [ [ 'filter', 'must be an object' ] ]
			)

		# If fields is not a list
		if 'fields' in req.data and \
			not isinstance(req.data['fields'], list):

			# Return an error
			return Error(
				errors.body.DATA_FIELDS, [ [ 'fields', 'must be a list' ] ]
			)

		# Search based on the req.data passed
		lRecords = [
			d['_id'] \
			for d in User.search(req.data['filter'], raw = [ '_id' ])
		]

		# If we got something, fetch the records from the cache
		if lRecords:
			lRecords = User.cache(
				lRecords,
				raw = ('fields' in req.data and req.data['fields'] or True)
			)

		# Remove the passwd
		for d in lRecords:
			del d['passwd']

		# Return the results
		return Response(lRecords)

	def session_read(self, req: jobject) -> Response:
		"""Session

		Returns the ID of the user logged into the current session

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""
		return Response({
			'user' : {
				'_id': req.session.user._id
			},
			'portal': req.session['portal']
		})

	def signin_create(self, req: jobject) -> Response:
		"""Signin

		Signs a user into the system

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Result
		"""

		# Check minimum fields
		try: evaluate(req.data, [ 'email', 'passwd' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Look for the user by alias
		oUser = User.filter({ 'email': req.data['email'] }, limit=1)
		if not oUser:
			return Error(errors.SIGNIN_FAILED)

		# If it's the system user, reject it
		if oUser['_id'] == users.SYSTEM_USER_ID:
			return Error(errors.SIGNIN_FAILED)

		# Validate the password
		if not oUser.password_validate(req.data['passwd']):
			return Error(errors.SIGNIN_FAILED)

		# Check if the user has permissions in the given portal
		sPortal = 'portal' in req.data and \
					req.data['portal'] or \
					''
		dPerms = Permissions.get((oUser['_id'], sPortal), raw = [ 'user' ])

		# If we don't have permissions for the given portal
		if not dPerms:
			return Error(errors.BAD_PORTAL, sPortal)

		# Create a new session
		oSesh = memory.create('sesh:%s' % uuid.uuid4().hex)

		# Store the user ID and portal in th session
		oSesh['user'] = { '_id': oUser['_id'] }
		oSesh['portal'] = sPortal

		# Save the session
		oSesh.save()

		# Return the session ID, primary user data, and portal name
		return Response({
			'session': oSesh.key(),
			'user': oSesh['user'],
			'portal': oSesh['portal']
		})

	def signin_to_create(self, req: jobject) -> Response:
		"""Signin To

		Gets a new session for a different portal using the credentials of
		the user already signed in

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Store the user ID (and immediately validate we have a session)
		sUserID = req.session.user._id

		# Check if the user has permissions in the given portal
		sPortal = 'portal' in req.data and \
					req.data['portal'] or \
					''
		dPerms = Permissions.get(
			(sUserID, sPortal),
			raw=['user']
		)

		# If we don't have permissions for the given portal
		if not dPerms:
			return Error(errors.BAD_PORTAL, sPortal)

		# Create a new session
		oSesh = memory.create('sesh:%s' % uuid.uuid4().hex)

		# Store the user ID and portal in th session
		oSesh['user'] = { '_id': sUserID }
		oSesh['portal'] = sPortal

		# Save the session
		oSesh.save()

		# Return the session ID and portal name
		return Response({
			'session': oSesh.key(),
			'portal': oSesh['portal']
		})

	def signout_create(self, req: jobject) -> Response:
		"""Signout create

		Called to sign out a user and destroy their session

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Close the session so it can no longer be found/used
		if 'session' in req and req.session:
			req.session.close()

		# Return OK
		return Response(True)

	def signup_create(self, req: jobject) -> Response:
		"""Signup create

		Creates a new account for the email given. Uses the default \
		permissions based on the portal passed (permissions set in config)

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Get the passed portal or use the default empty string
		sPortal = 'portal' in req.data and \
					req.data.pop('portal') or \
					''

		# If there's no section in the config
		if sPortal not in self._conf['portals']:
			return Error(errors.BAD_CONFIG, 'portals.%s' % sPortal)

		# Check minimum required fields
		try: evaluate(req.data, [ 'email', 'g-recaptcha-response', 'url' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# If we're doing v3
		if self._conf['recaptcha']['version'] == 'v3':

			# Run the assessment
			dRes = self._recaptcha_v3(
				req.data.pop('g-recaptcha-response'),
				'signup'
			)

			# If the assessment failed
			if not dRes['result']:
				return Error(
					errors.body.DATA_FIELDS,
					[ 'g-recaptcha-response', dRes['reason'] ]
				)

		# Else, if we're doing v2
		elif self._conf['recaptcha']['version'] == 'v2':

			# Check the captcha (pop off the field from req.data)
			dRes = self._recaptcha_v2(
				req.data.pop('g-recaptcha-response'),
				get_client_ip(req.environment)
			)

			# If the captcha failed, return the errors
			if not dRes['success']:
				return Error(
					errors.body.DATA_FIELDS,
					[ [ 'g-recaptcha-response', dRes['error-codes'] ] ]
				)

		# Else
		else:
			return Error(
				errors.BAD_CONFIG, [ 'recaptcha.version', 'must be v2 or v3' ]
			)

		# Make sure the URL has the {key} field
		if '{key}' not in req.data['url']:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'url', 'missing "{key}"' ] ]
			)

		# Pop off the URL
		sURL = req.data.pop('url')

		# Strip leading and trailing spaces on the email
		req.data['email'] = req.data['email'].strip()

		# Make sure the email is valid structurally
		if not regex.EMAIL_ADDRESS.match(req.data['email']):
			return Error(
				errors.body.DATA_FIELDS, [ [ 'email', 'invalid' ] ]
			)

		# Check if a user with that email already exists
		sID = User.exists(req.data['email'], 'email')

		# Flag to send setup email
		bSetup = False

		# If the user already exists
		if sID:

			# Check for existing permissions on that given portal
			dPerms = Permissions.get(( sID, sPortal ), raw = [ 'user' ])

			# If the user already has an account with the portal
			if dPerms:
				return Error(
					errors.body.DB_DUPLICATE, [ req.data['email'] , 'user' ]
				)

		# Else, this is a new user
		else:

			# Add the blank password
			req.data['passwd'] = users.EMPTY_PASS

			# Add defaults
			if 'locale' not in req.data:
				req.data['locale'] = self._conf['user_default_locale']

			# Validate by creating a Record instance
			try:
				oUser = User(req.data)
			except ValueError as e:
				return Error(errors.body.DATA_FIELDS, e.args[0])

			# Create the record
			sID = oUser.create(changes = { 'user': users.SYSTEM_USER_ID })

			# Send the setup email
			bSetup = True

		# If the record was created (or already existed)
		if sID:

			# Create the permissions
			try:
				oPerms = Permissions({
					'user': sID,
					'portal': sPortal,
					'rights': self._conf['portals'][sPortal]['rights']
				})
			except ValueError as e:
				return Error(
					errors.BAD_CONFIG,
					[ 'portals.%s.rights' % sPortal, e.args[0] ]
				)

			if not oPerms.create(changes = { 'user': users.SYSTEM_USER_ID }):
				oUser.delete(changes = { 'user': users.SYSTEM_USER_ID })
				return Error(errors.body.DB_CREATE_FAILED, 'permissions')

		# If we need to send the setup email for a new user
		if bSetup:

			# Create key for setup validation
			sSetupKey = self._create_key(sID, 'setup')

			# Email the user the setup link
			oResponse = create('mouth', 'email', { 'data': {
				'template': {
					'name': 'setup_user',
					'locale': oUser['locale'],
					'portal': sPortal,
					'variables': {
						'key': sSetupKey,
						'url': sURL.replace('{key}', sSetupKey)
					},
				},
				'to': req.data['email']
			}}, access.generate_key())
			if oResponse.error:
				Key.delete_get(sSetupKey)
				return oResponse

			# Send the ID
			return Response(sID)

		# Else, just send True
		else:
			return Response(True)

	def user_create(self, req: jobject) -> Response:
		"""User create

		Creates a new user

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check internal or verify
		iWhich = self._internal_or_verify(req, 'brain_user', access.CREATE)

		# Set the session user based on the mode of access
		sSessionUser = iWhich == access.INTERNAL and \
						users.SYSTEM_USER_ID or \
						req.session.user._id

		# If we are missing the email
		if 'email' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'email', 'missing' ] ]
			)

		# If the verified flag is not set
		if 'verified' not in req.data:
			req.data['verified'] = False

		# Get the passed portal or use the default empty string
		sPortal = 'portal' in req.data and \
					req.data.pop('portal') or \
					''

		# If we are not verified
		if not req.data['verified']:

			# If the url is missing
			if 'url' not in req.data:
				return Error(
					errors.body.DATA_FIELDS, [ [ 'url', 'missing' ] ]
				)

			# Make sure the URL has the {key} field
			if '{key}' not in req.data['url']:
				return Error(
					errors.body.DATA_FIELDS, [ [ 'url', 'missing "{key}"' ] ]
				)

			# Pop off the URL
			sURL = req.data.pop('url')

		# Strip leading and trailing spaces on the email
		req.data['email'] = req.data['email'].strip()

		# Make sure the email is valid structurally
		if not regex.EMAIL_ADDRESS.match(req.data['email']):
			return Error(
				errors.body.DATA_FIELDS, [ [ 'email', 'invalid' ] ]
			)

		# Check if a user with that email already exists
		sExistingUserID = User.exists(req.data['email'], 'email')
		if sExistingUserID:
			return Error(
				errors.body.DB_DUPLICATE, [ req.data['email'], 'user' ]
			)

		# Add the blank password
		req.data['passwd'] = users.EMPTY_PASS

		# Add defaults
		if 'locale' not in req.data:
			req.data['locale'] = self._conf['user_default_locale']

		# Validate by creating a Record instance
		try:
			oUser = User(req.data)
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, e.args[0])

		# Create the record
		sID = oUser.create(changes = { 'user': sSessionUser })

		# If the record was created
		if sID:

			# If the user is not verified
			if not oUser['verified']:

				# Create key for setup validation
				sSetupKey = self._create_key(oUser['_id'], 'setup')

				# Email the user the setup link
				oResponse = create('mouth', 'email', { 'data': {
					'template': {
						'name': 'setup_user',
						'locale': oUser['locale'],
						'portal': sPortal,
						'variables': {
							'key': sSetupKey,
							'url': sURL.replace('{key}', sSetupKey)
						},
					},
					'to': req.data['email']
				}}, access.generate_key())
				if oResponse.error:
					Key.delete_get(sSetupKey)
					return oResponse

		# Return the result
		return Response(sID)

	def user_read(self, req: jobject) -> Response:
		"""User Read

		Fetches an existing user and returns their data

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# If there's an ID, check permissions
		if 'data' in req and '_id' in req.data:
			self._verify(
				(req.session.user._id, req.session['portal']),
				'brain_user',
				access.READ
			)

			# If no portal was passed
			if 'portal' not in req.data:
				req.data['portal'] = ''

		# Else, assume the signed in user's Record
		else:
			req.data = {
				'_id': req.session.user._id,
				'portal': req.session['portal']
			}

		# Fetch it from the cache
		dUser = User.cache(req.data['_id'], raw=True)

		# If it doesn't exist
		if not dUser:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['_id'], 'user' ]
			)

		# Remove the passwd
		del dUser['passwd']

		# Fetch the permissions and add them to the user if they're found
		dPermissions = Permissions.get(
			(req.data['_id'], req.data['portal']),
			raw=['rights']
		)

		dUser['permissions'] = dPermissions and dPermissions['rights'] or None

		# Return the user data
		return Response(dUser)

	def user_update(self, req: jobject) -> Response:
		"""User Update

		Updates an existing user

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# If there's an ID, check permissions
		if '_id' in req.data and \
			req.data['_id'] != req.session.user._id:

			# If the ID isn't set
			if not req.data['_id']:
				return Error(
					errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ]
				)

			# Make sure the user has the proper permission to do this
			self._verify(
				(req.session.user._id, req.session['portal']),
				'brain_user',
				access.UPDATE
			)

		# Else, assume the signed in user's Record
		else:
			req.data['_id'] = req.session.user._id

		# Fetch it from the cache
		oUser = User.cache(req.data['_id'])

		# If the user isn't found
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['_id'], 'user' ]
			)

		# Remove fields that can't be changed
		for k in [ '_id', '_created', '_updated', 'email', 'passwd' ]:
			try: del req.data[k]
			except KeyError: pass

		# If the email was passed
		if 'email' in req.data:

			# Strip leading and trailing spaces
			req.data['email'] = req.data['email'].strip()

			# Make sure it's valid structurally
			if not regex.EMAIL_ADDRESS.match(req.data['email']):
				return Error(
					errors.body.DATA_FIELDS, [ [ 'email', 'invalid' ] ]
				)

		# Step through each field passed and update/validate it
		lErrors = []
		for f in req.data:
			try: oUser[f] = req.data[f]
			except ValueError as e: lErrors.extend(e.args[0])

		# If there was any errors
		if lErrors:
			return Error(errors.body.DATA_FIELDS, lErrors)

		# Update the record
		bRes = oUser.save(changes = { 'user': req.session.user._id })

		# If it was updated, clear the cache
		if bRes:
			User.clear(oUser['_id'])

		# Return the result
		return Response(bRes)

	def user_email_update(self, req: jobject) -> Response:
		"""User Email update

		Changes the email for the current signed in user

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ 'email', 'email_passwd', 'url' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Make sure the URL has the {key} field
		if '{key}' not in req.data['url']:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'url', 'missing {key}' ] ]
			)

		# Find the user
		oUser = User.get(req.session.user._id)
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD,
				[ req.session.user._id, 'user' ]
			)

		# Validate the password
		if not oUser.password_validate(req.data['email_passwd']):
			return Error(errors.SIGNIN_FAILED)

		# If the email hasn't changed
		if oUser['email'] == req.data['email']:
			return Response(False)

		# Strip leading and trailing spaces on email
		req.data['email'] = req.data['email'].strip()

		# Make sure the email is valid structurally
		if not regex.EMAIL_ADDRESS.match(req.data['email']):
			return Error(
				errors.body.DATA_FIELDS, [ [ 'email', 'invalid' ] ]
			)

		# Look for someone else with that email
		dUser = User.filter({ 'email': req.data['email'] }, raw = ['_id'])
		if dUser:
			return Error(
				errors.body.DB_DUPLICATE, [ req.data['email'], 'user' ]
			)

		# Update the email and verified fields
		try:
			oUser['email'] = req.data['email']
			oUser['verified'] = False
		except ValueError as e:
			return Error(errors.body.DATA_FIELDS, e.args[0])

		# Generate a new key
		sKey = self._create_key(oUser['_id'], 'verify')

		# Update the user
		bRes = oUser.save(changes = { 'user':req.session.user._id })

		# If the user was updated
		if bRes:

			# Clear the cache
			User.clear(oUser['_id'])

			# Create key
			sKey = self._create_key(oUser['_id'], 'verify')

			# Verification template variables
			dTpl = {
				'key': sKey,
				'url': req.data['url'].replace('{key}', sKey)
			}

			# Email the user the key
			oResponse = create('mouth', 'email', { 'data': {
				'template': {
					'name': 'verify_email',
					'locale': oUser['locale'],
					'variables': dTpl
				},
				'to': req.data['email'],
			}}, access.generate_key())
			if oResponse.error:
				Key.delete_get(sKey)
				return oResponse

		# Return the result
		return Response(bRes)

	def user_email_verify_update(self, req: jobject) -> Response:
		"""User Email Verify update

		Marks the user/email as verified

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# If the key is not passed
		if 'key' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'key', 'missing' ] ]
			)

		# Look for the key
		oKey = Key.get(req.data['key'])
		if not oKey:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['key'], 'key' ]
			)

		# Find the user associated with they key
		oUser = User.get(oKey['user'])
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD, [ oKey['user'], 'user' ]
			)

		# Mark the user as verified and save
		oUser['verified'] = True
		bRes = oUser.save(changes = { 'user': oKey['user'] })

		# If the save was successful
		if bRes:

			# Clear the cache
			User.clear(oKey['user'])

			# Delete the key
			oKey.delete()

		# Return the result
		return Response(bRes)

	def user_names_read(self, req: jobject) -> Response:
		"""User Names read

		Returns a list or dict of IDs to names of users

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Make sure we got an ID
		if '_id' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ]
			)

		# If the type is missing
		if 'type' not in req.data or not req.data['type']:
			req.data['type'] = 'object'

		# Else, if the type is invalid
		elif req.data['type'] not in ['array', 'object']:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'type', 'invalid' ] ]
			)

		# If we only got one ID
		if isinstance(req.data['_id'], str):
			req.data['_id'] = [ req.data['_id'] ]

		# If the list is empty
		if not req.data['_id']:
			return Error(
				errors.body.DATA_FIELDS, [ [ '_id', 'empty' ] ]
			)

		# If the client requested an array, return a list
		if req.data['type'] == 'array':
			return Response(
				User.get(
					req.data['_id'],
					raw = [ '_id', 'first_name', 'last_name' ],
					orderby = [ 'first_name', 'last_name' ]
				)
			)

		# Else, they requested an object, so return a dict
		else:
			return Response({
				d['_id']: {
					'first_name': d['first_name'],
					'last_name': d['last_name']
				} \
				for d in User.get(
					req.data['_id'],
					raw = [ '_id', 'first_name', 'last_name' ]
				)
			})

	def user_passwd_update(self, req: jobject) -> Response:
		"""User Password update

		Changes the password for the current signed in user

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Make sure we got a new password
		if 'new_passwd' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'new_passwd', 'missing' ] ]
			)

		# If the id is passed
		if '_id' in req.data and req.data['_id'] is not None:

			# If it doesn't match the logged in user, check permissions
			if req.data['_id'] != req.session.user._id:
				self._verify(
					(req.session.user._id, req.session['portal']),
					'brain_user',
					access.UPDATE
				)

		# Else, use the user from the session
		else:

			# If the old password is missing
			if 'passwd' not in req.data:
				return Error(
					errors.body.DATA_FIELDS, [ [ 'passwd', 'missing' ] ]
				)

			# Store the session as the user ID
			req.data['_id'] = req.session.user._id

		# Find the user
		oUser = User.get(req.data['_id'])
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['_id'], 'user' ]
			)

		# If we have an old password
		if 'passwd' in req.data:

			# Validate it
			if not oUser.password_validate(req.data['passwd']):
				return Error(
					errors.body.DATA_FIELDS, [ [ 'passwd', 'invalid' ] ]
				)

		# Make sure the new password is strong enough
		if not User.password_strength(req.data['new_passwd']):
			return Error(errors.PASSWORD_STRENGTH)

		# Set the new password and save
		oUser['passwd'] = User.password_hash(req.data['new_passwd'])
		oUser.save(changes = { 'user': req.session.user._id })

		# Return OK
		return Response(True)

	def user_passwd_forgot_create(self, req: jobject) -> Response:
		"""User Password Forgot create

		Creates the key that will be used to allow a user to change their \
		password if they forgot it

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, ['email', 'url'])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Make sure the URL has the {key} field
		if '{key}' not in req.data['url']:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'url', 'missing {key}' ] ]
			)

		# Look for the user by email
		dUser = User.filter(
			{'email': req.data['email']},
			raw = ['_id', 'locale'],
			limit = 1
		)
		if not dUser:
			return Response(False)

		# Generate a key
		sKey = self._create_key(dUser['_id'], 'forgot')

		# Forgot email template variables
		dTpl = {
			'key': sKey,
			'url': req.data['url'].replace('{key}', sKey)
		}

		# Email the user the key
		oResponse = create('mouth', 'email', { 'data': {
			'template': {
				'name': 'forgot_password',
				'locale': dUser['locale'],
				'variables': dTpl
			},
			'to': req.data['email'],
		}}, access.generate_key())
		if oResponse.error:
			Key.delete_get(sKey)
			return oResponse

		# Return OK
		return Response(True)

	def user_passwd_forgot_update(self, req: jobject) -> Response:
		"""User Password Forgot update

		Validates the key and changes the password to the given value

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ 'passwd', 'key' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Look up the key
		oKey = Key.get(req.data['key'])
		if not oKey:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['key'], 'key' ]
			)

		# Make sure the new password is strong enough
		if not User.password_strength(req.data['passwd']):
			return Error(errors.PASSWORD_STRENGTH)

		# Find the User
		oUser = User.get(oKey['user'])
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD, [ oKey['user'], 'user' ]
			)

		# Store the new password, mark verified, and update
		oUser['passwd'] = User.password_hash(req.data['passwd'])
		oUser['verified'] = True
		oUser.save(changes=False)

		# Delete the key
		oKey.delete()

		# Return OK
		return Response(True)

	def user_setup_key_read(self, req: jobject) -> Response:
		"""User Setup Key read

		Generates a usable setup key for a user. Only accessible internally

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Verify the key, remove it if it's ok
		access.internal(req.data)

		# If the ID is missing
		if '_id' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ]
			)

		# Create key for setup validation and return it
		return Response(
			self._create_key(req.data['_id'], 'setup')
		)

	def user_setup_read(self, req: jobject) -> Response:
		"""User Setup read

		Validates the key exists and returns the user's info

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# If the key is missing
		if 'key' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'key', 'missing' ] ]
			)

		# Look up the key
		dKey = Key.get(req.data['key'], raw=True)
		if not dKey:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['key'], 'key' ]
			)

		# Get the user
		dUser = User.get(dKey['user'], raw=True)
		if not dUser:
			return Error(
				errors.body.DB_NO_RECORD, (dKey['user'], 'user')
			)

		# Delete unnecessary fields
		for k in [ '_id', '_created', '_updated', 'passwd', 'verified' ]:
			del dUser[k]

		# Return the user
		return Response(dUser)

	def user_setup_send_create(self, req: jobject) -> Response:
		"""User Setup Send create

		Used to re-send the setup email message to a user in case they never
		got it

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check internal or verify
		iWhich = self._internal_or_verify(
			req, 'brain_user', [ access.CREATE, access.UPDATE ]
		)

		# Verify the minimum fields
		try: evaluate(req.data, ['_id', 'url'])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Make sure the URL has the {key} field
		if '{key}' not in req.data['url']:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'url', 'missing "{key}"' ] ]
			)

		# Pop off the URL
		sURL = req.data.pop('url')

		# Find the user
		dUser = User.get(req.data['_id'], raw = True)
		if not dUser:
			return Error(
				errors.body.DB_NO_RECORD, [ req.data['_id'], 'user' ]
			)

		# If the user is already setup
		if dUser['passwd'] != users.EMPTY_PASS:
			return Error(errors.body.ALREADY_DONE)

		# Create key for setup validation
		sSetupKey = self._create_key(dUser['_id'], 'setup')

		# Email the user the setup link
		oResponse = create('mouth', 'email', {'data': {
			'template': {
				'name': 'setup_user',
				'locale': dUser['locale'],
				'variables': {
					'key': sSetupKey,
					'url': sURL.replace('{key}', sSetupKey)
				},
			},
			'to': dUser['email']
		}}, access.generate_key())
		if oResponse.error:
			Key.delete_get(sSetupKey)
			return oResponse

		# Return OK
		return Response(True)

	def user_setup_update(self, req: jobject) -> Response:
		"""User Setup update

		Finishes setting up the account for the user by setting their password \
		and verified fields

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Verify the minimum fields
		try: evaluate(req.data, [ 'passwd', 'key' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ]
			)

		# Look up the key
		oKey = Key.get(req.data['key'])
		if not oKey:
			return Error(
				errors.body.DB_NO_RECORD, (req.data['key'], 'key')
			)
		req.data.pop('key')

		# If there's a portal
		sPortal = 'portal' in req.data and req.data.pop('portal') or ''

		# Find the user
		oUser = User.get(oKey['user'])
		if not oUser:
			return Error(
				errors.body.DB_NO_RECORD, [ oKey['user'], 'user' ]
			)

		# Make sure the new password is strong enough
		if not User.password_strength(req.data['passwd']):
			return Error(errors.PASSWORD_STRENGTH)

		# Pop off the password
		sPassword = req.data.pop('passwd')

		# Go through the remaining fields and attempt to update
		lErrors = []
		for k in req.data:
			try: oUser[k] = req.data[k]
			except ValueError as e: lErrors.extend(e.args[0])
		if lErrors:
			return Error(errors.body.DATA_FIELDS, lErrors)

		# Set the new password, mark as verified, and save
		oUser['passwd'] = User.password_hash(sPassword)
		oUser['verified'] = True
		oUser.save(changes = { 'user': oKey['user'] })

		# Delete the key
		oKey.delete()

		# Create a new session, store the user ID and portal, and save it
		oSesh = memory.create()
		oSesh['user'] = {'_id': oUser['_id']}
		oSesh['portal'] = sPortal
		oSesh.save()

		# Return the session ID
		return Response(oSesh.key())

	def users_by_email_read(self, req: jobject) -> Response:
		"""Users By E-Mail read

		Finds a user given their unique email address

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check internal or verify
		self._internal_or_verify(req, 'brain_user', access.READ)

		# If we are missing the ID
		if 'email' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ 'email', 'missing' ] ]
			)

		# If the fields are passed
		if 'fields' in req.data:

			# If it's not a list
			if not isinstance(req.data['fields'], list):
				return Error(
					errors.body.DATA_FIELDS,
					[ [ 'fields', 'must be an array' ] ]
				)

		# Else, set default fields
		else:
			req.data['fields'] = [ '_id', 'email', 'first_name', 'last_name' ]

		# If the order is passed
		if 'order' in req.data:

			# If it's not a list
			if not isinstance(req.data['order'], list):
				return Error(
					errors.body.DATA_FIELDS, [ [ 'order', 'must be an array' ] ]
				)

		# Else, set default fields
		else:
			req.data['order'] = [ 'first_name', 'last_name' ]

		# If we only got one email
		mLimit = isinstance(req.data['email'], str) and 1 or None

		# Find and return the user(s)
		return Response(
			User.filter(
				{ 'email': req.data['email'] },
				raw = req.data['fields'],
				orderby = req.data['order'],
				limit = mLimit
			)
		)

	def users_by_id_read(self, req: jobject) -> Response:
		"""Users By ID read

		Finds all users with a specific id

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check internal or verify
		self._internal_or_verify(req, 'brain_user', access.READ)

		# If we are missing the ID
		if '_id' not in req.data:
			return Error(
				errors.body.DATA_FIELDS, [ [ '_id', 'missing' ] ]
			)

		# If the fields are passed
		if 'fields' in req.data:

			# If it's not a list
			if not isinstance(req.data['fields'], list):
				return Error(
					errors.body.DATA_FIELDS,
					[ [ 'fields', 'must be an array' ] ]
				)

		# Else, set default fields
		else:
			req.data['fields'] = [ '_id', 'email', 'first_name', 'last_name' ]

		# If the order is passed
		if 'order' in req.data:

			# If it's not a list
			if not isinstance(req.data['order'], list):
				return Error(
					errors.body.DATA_FIELDS, [ [ 'order', 'must be an array' ] ]
				)

		# Else, set default fields
		else:
			req.data['order'] = [ 'first_name', 'last_name' ]

		# Find and return the users
		return Response(
			User.get(
				req.data['_id'],
				raw = req.data['fields'],
				orderby = req.data['order']
			)
		)

	def verify_read(self, req: jobject) -> Response:
		"""Verify read

		Checks the user currently in the session has access to the requested
		permission

		Arguments:
			req (jobject): The request details, which can include 'data', \
				'environment', and 'session'

		Returns:
			Services.Response
		"""

		# Check minimum fields
		try: evaluate(req.data, [ 'name', 'right' ])
		except ValueError as e:
			return Error(
				errors.body.DATA_FIELDS, [ [ f, 'missing' ] for f in e.args ])

		# Verify and return the result
		return Response(
			self._verify(
				(req.session.user._id, req.session['portal']),
				req.data['name'],
				req.data['right'],
				'id' in req.data and req.data['id'] or None
			)
		)