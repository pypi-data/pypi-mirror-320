=========
Changelog
=========

Version 0.6
===========

 * Add the ability to send raw states to Hubspace and have the tracked device update

Version 0.5.1
=============

 * Fixed an issue where the account ID wouldnt be set during a partial initialization

Version 0.5.0
=============

 * Only emit updates to subscribers if values have changed
 * Fixed an issue where the logger was always in debug


Version 0.4.1
=============

 * Adjusted logic for how HubspaceDevice modified models
 * Fixed an issue around Device initialization

Version 0.4.0
=============

 * Added tracking for BLE and MAC addresses
 * Added binary sensors

Version 0.3.7
=============

 * Fixed an issue around subscribers with deletion

Version 0.3.6
=============

 * Fixed an issue around switches not properly subscribing to updates
 * Fixed an issue where Hubspace could return a session reauth token when preparing a new session
 * Added models for HPSA11CWB and HPDA110NWBP

Version 0.3.0
=============

 * Fixed an issue around subscribers with deletion



Version 0.2
===========

 * Added support for Binary Sensors
 * Fixed an issue where a dimmer switch could not be dimmed

Version 0.2
===========

 * Added support for Sensors

Version 0.1
===========

 * Initial implementation
 * Rename from hubspace_async to aiohubspace
 * Utilize the concept of a bridge instead of raw connection
