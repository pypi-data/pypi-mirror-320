# NSight Data Extraction API wrapper/Library

WARNING/NOTE: I wrote all of this based on the N-Able documentation, which says N-Able all over it, but I am now realising this is technically just for N-Sight, not N-Able.  I am in the process of renaming and fixing all of the issues this causes.

This is a Python wrapper/library for the NSight Data Extraction API.  The NSight API returns data in xml format, this tool will convert those to lists and dictionaries for ease of use.

The official API documentation from NSight can be found [here](https://documentation.n-able.com/remote-management/userguide/Content/api_calls.htm). I have tried to keep my naming scheme similar to theirs.

NOTE:  
- This is still in extremely early stages of development, function names may change! 

## Table Of Contents
*I don't know how to make this yet, so it's Coming Soon*


## Installation

```
pip install NAbleAPI
```

## Getting Started

To use the NAble API, you will need to know your region and have an API key.

1. Import the package
2. Get an API key. Follow [these instructions](https://documentation.n-able.com/remote-management/userguide/Content/api_key.htm) to get your API key.
3. Find your region (see below)


### Regions

To find your region, check [this page](https://documentation.n-able.com/remote-management/userguide/Content/determine_url.htm) or view table below. 

Notes: 
- Not all regions have been tested, if your region is marked 'untested' on the table below, please let me know whether it works.
- If your dashboard URL starts with `www2`, assume it is just `www` for the region.
- If there is another abbreviation or country code you would like added, let me know!

| Dashboard URL | Region | Status |
| --- | --- | --- |
| www.am.remote.management | americas, ams | Untested |
| wwwasia.system-monitor.com | asia | Untested |
| www.system-monitor.com | australia, au, aus | Untested |
| wwweurope1.systemmonitor.eu.com | europe, eu | Untested |
| wwwfrance.systemmonitor.eu.com | france, fr | Untested |
| wwwfrance1.systemmonitor.eu.com | france1, fr1 | Untested |
| wwwgermany1.systemmonitor.eu.com | germany, de, deu | Untested |
| wwwireland.systemmonitor.eu.com | ireland, ie, irl | Untested |
| wwwpoland1.systemmonitor.eu.com | poland, pl,pol | Untested |
| www.systemmonitor.co.uk | united kingdom, uk, gb, gbr | **Verified** |
| www.systemmonitor.us | united states, us, usa | Untested |

### Using the package


#### Create a new .py file in the root directory and import the NAble package
```
from NAbleAPI import NAble
```

#### Authenticate with your API key
```
na = NAble('[YOUR REGION]','[YOUR API KEY]')
```

Example

```
na = NAble('uk','f821213a8d3q43843dj39824')
```

(Not a real API key, don't try to use it)


#### Make your first request
Gee it sure would be helpful is there was documentation for the available commands.  Unfortunately, there isn't right now.

Get all your clients

```
myNAbleClients = na.clients()
```


#### Storing your key
It's probably best not to store your API key in your script. Instead, you can create a .env file and use that.

1. Create a new file called `.env` in the root directory
2. Put your API key in it (do not put it in quotes, type exactly as shown below)
```
NABLE_KEY = f821213a8d3q43843dj39824
```
3. Get the key from file
``` 
from NAbleAPI import NAble # Import the NAble package
import os # Import OS package (built into Python, I'm like 99% sure)

NABLE_KEY = os.getenv("NABLE_KEY")

na = NAble('uk',NABLE_KEY)
```

## API Endpoints
The endpoints are grouped by category on NAble's website, so I have done the same below.
I found the names on NAbles site to be a bit long, so I have shortened them a bit. The `Function Name` is what you will use in Python.
I'm doing my best to get them all added!



### Clients, SItes, and Devices 
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/devices.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_clients | Working | clients() | List all clients |
| list_sites | Working | sites() | List sites for a client |
| list_servers | Working | servers() | list servers at a site |
| list_workstations | Working | workstations() | list workstations at a site |
| list_agentless_assets | Working | agentlessAssets() | List agentless assets at a site |
| list_devices_at_client | Working | clientDevices() | List all workstations or servers for a client |
| list_device_monitoring_details | Working | deviceDetails() | Get details for a single device | 
| add_client | Working | addClient() | Add a client |
| add_site | Working | addSite() | Add a site | 
| get_site_installation_package() | Partially Working | siteInstallPackage | Create/Get a site installation package (returns rawbytes right now) |

### Checks and results
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/checks_and_results.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_checks | Working | checks() |  List all checks for a device |
| list_failing_checks | Working | failingChecks() | List all failing checks |
| list_check_config | Working | checkConfig() | Get a single checks configuration |
| get_formatted_check_output | Working | formattedCheckOutput() | Get first line of check result |
| list_outages | Working | checks() | List all outages for a device |
| list_performance_history | Untested | performanceHistory() |  Get performance history of a device |
| list_drive_space_history | Working | driveSpaceHistory() |  Get Device Storage History |
| list_exchange_storage_history | Untested | exchangeStorageHistory() | Get Exchange Storage History |
| clear_check | Untested | clearCheck() | Clear a check |
| add_check_note | Working | addNote() | Add note to a check |
| list_templates | Working | templates() | List all server/workstation monitoring templates |

### Anti-Virus Update Check Information
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/api_av_info.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_supported_av_products | Working | supportedAVs() | Lists supported AVs |
| list_av_definitions | Working | AVDefinitions() | Get definitions for specific AV Product |
| get_av_definition_release_date | Working | AVDefinitionsReleaseDate() | Get release date of specific AV version |
| list_av_history | Working | AVHistory() | List last 60s of AV status (I got 90 though...) |

### List Backup Check History
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/list_backup_history.htmm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_backup_history | Untested | backupHistory() | Get last 60 days of backup history for device |

### Asset Tracking Information
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/asset_tracking_information.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_all_hardware | Working | assetHardware() | Get all hardware for an asset |
| list_all_software | Working | assetSoftware() | Get all software for an asset |
| list_license_groups | Working | licenseGroups() | Get software license groups for account |
| list_license_groups | Working | licenseGroupItems() | Get all software license groups for account/tenant |
| list_license_group_items | Working | clientLicenseCount() | Get software in a software license group |
| list_client_license_count | Untested | assetLicensedSoftware() | Get client software license counts |
| list_device_asset_details | Working | assetDetails() | Get asset information from device ID |



### Settings
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/settings.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| list_wallchart_settings | Working | wallchartSettings() | Get general wallchart settings |
| list_general_settings | Working | generalSettings() | Get general account settings |

### Patch Management
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/patch_management.htm)

These may be moved to their own subclass in the future!

| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| patch_list_all | Working | listPatches() | List all patches for a device |
| patch_approve | Working | approvePatches() | Approve patch(es) for a device |
| patch_do_nothing | Working | doNothingPatches() | Do nothing on patch(es) for a device |
| patch_ignore | Working | ignorePatches() | Ignore patch(es) for a device |
| patch_reprocess | Working | reprocessPatches() | Reprocess patch(es) for a device |
| patch_retry | Working | retryPatches() | Retry patch(es) for a device (think this is the same as reprocess) |

### Managed Anti-Virus
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/managed_antivirus2.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |
| mav_quarantine_list | Untested | mavQuarantine() | Get quarantined threats for a device |
| mav_quarantine_release | Untested | mavQuarantineRelease() | Release threat(s) from Managed Antivirus quarantine |
| mav_quarantine_remove | Untested | mavQuarantineRemove() | Remove threat(s) from Managed Antivirus quarantine |
| mav_scan_start | Working | mavScanStart() | Start quick scan on a device |
| mav_scan_pause | Working | mavScanPause() | Pause scan on a device |
| mav_scan_resume | Working | mavScanResume() | Resume/unpause scan on a device |
| mav_scan_cancel | Working | mavScanCancel() | Cancel scan on a device |
| mav_scan_device_list | Working | mavScanList() | Get a list of scans for a device |
| list_mav_scans | Working | mavScans() | Get a list of scans for a device |
| list_mav_threats | Working | mavThreats() | Get the most recent occurence of each threat found on a device |
| list_mav_quarantine | Untested | mavQuarantineList() | ??? |
| mav_definitions_update | Working | mavUpdate() | Update the bitdefender definitions on a device |

### Backup & Recovery
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/api_mob_over.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |

### Run Task Now
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/run_task_now.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |

### List Active Directory Users
Official NAble documentation page [here](https://documentation.n-able.com/remote-management/userguide/Content/list_active_directory_users.htm)
| Service | Status | Function Name | Description |
| --- | --- | --- | --- |

