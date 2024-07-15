## Subscription Importer

Imports subscriptions from an csv file into a youtube account. This is useful for transferring youtube subscriptions from one youtube account to another.

## Usage

1. Get the properly formatted csv file from the account you wish to transfer subscriptions from

	- Open [Google Takeout](https://takeout.google.com/takeout/custom/youtube)
	- Check if you are on the right account
	- Under `Create a new export` choose `YouTube and YouTube Music`
	- Click on `All YouTube data included` and only tick `subscriptions` in the dialog that opens
	- Click on `Next step`, make sure `Export once` is chosen and click on `Create export`
	- Wait until the export creation is finished, then on the same page click on `Download` under `Your latest export` that should now be visible
	- Extract the downloaded archive and find the file `subscriptions.csv`
	- While logged into your Invidious account go to Subscriptions -> Manage Subscriptions -> Import/Export -> Import YouTube subscriptions, select the file you just downloaded and click on `Import`

2. Get authenticated, since this requires access to your google account you must generate the correct `client_secrets.json` file

	- Create project in the [Developer Console](https://console.developers.google.com/apis/dashboard)
	- Next register for YouTube API, go to the project you just created and in the [Developer Console](https://console.developers.google.com/apis/dashboard)
	- Go to the [API Library](https://console.developers.google.com/apis/library) and turn __YouTube Data API__ to __ON__
	- Download JSON credentials, go to __Credentials__ if not created already, create one must be __OAuth 2.0__. Select the created credential and click on __Download JSON__
	- Rename the downloaded JSON file to `client_secrets.json` and drag into this root directory, must be in the same folder as `subscribe.py`
	
3. Make sure all required packages are installed before running

	To do this I recommend using a [virtual environment](https://virtualenv.pypa.io/en/stable/)
	
	```bash
	$ virtualenv -p python3 env
	$ source env/bin/activate
	$ pip install -r requirements.txt
	
	```

4. Run the script
	
	To do this either drag the exported xml file from step 1 into this root directory and name it `subscriptions.csv` or run the script with this argument
	
	```bash
	$ python3 subscribe.py --csv /path/to/csv/file.csv
	```
	
	
	
## Limitations

There is a request cap every few hours, I believe the cap is around ~70 subscriptions per few hours. So you may have to run the script several times before being able to fully import everything. I have not yet figured out a way around this.
