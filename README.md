<h1>:robot: Scraper w/ Discord Notification</h1>

A web scraper for Kijiji.ca based on your desired searches. You can also use excludes to prevent any unrelated items from triggering the notification script.
All notifications will be sent to your desired Discord channel via webhook.
*Tested on Ubuntu 18.04.03 LTS.*

A lot of credit goes to @CRutkowski for his Kijiji-Scraper project (https://github.com/CRutkowski/Kijiji-Scraper) that served as the base for mine.

![Scraper - Notification - Embed](https://user-images.githubusercontent.com/58180427/69883816-73c8ed00-129b-11ea-9dd8-c02a9fbb76e2.png)


<h2>Installation</h2>

Make sure that your machine is up to date.
>$ sudo apt update

>$ sudo apt upgrade

Use git to pull the repository files to your machine in the /github/ directory:
>$ sudo git clone https://github.com/suppaduppax/Scraper-Discord-Notification.git

Install some required packages:
>$ sudo apt install python3-pip python3-bs4

Install some required packages for python:
>$ sudo -H pip3 install -r /github/Scraper-Discord-Notification/requirements.txt

<h2>Setup</h2>

Give main.py executable permissions.
>$ sudo chmod +x /github/Scraper-Discord-Notification/main.py

Give ads.json write permissions so that old ads can be stored.
>$ sudo chmod a+w /github/Scraper-Discord-Notification/ads.json

<h3>Get a Discord Webhook</h3>

Check out: https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks

**webhook:** insert the url provided by Discord. No quotations.
**bot name:** the name you want your webhook to use. No quotations.

To get a search URL, go to http://www.kijiji.ca and use the search box for the item you're looking for.

![Kijiji - Search](https://user-images.githubusercontent.com/58180427/69773229-dd3fe300-1157-11ea-884c-5f5c12b3f874.png)

Use any of the filters on the left hand side of the page to narrow down your search as closely as you want (e.g. regions, price, etc.).

![Kijiji - URL](https://user-images.githubusercontent.com/58180427/69773238-e16c0080-1157-11ea-8105-797037bb5687.png)

<h3>Initial Start-Up (Optional)</h3>

<h4>Add a Notification Agent<h4>
> sudo python3 main.py notification-agent add
Notification agents are what will be used to notify you when new ads are found.
Right now, only discord is supported more will he more added in the future.
 
<h4>Add a Source<h4>
> sudo python3 main.py source add
Sources contain the configuration that will be used when doing the actual scraping. Right
now only the kijiji module is supported but more will be added in the future.

<h4>Add a Task<h4>
> sudo python3 main.py task add
Tasks are what executes the scraping process and runs the notification.
You can set the frequency of these tasks which will use cron to run them on
a schedule.

<h4>Dry-runs and Priming<h4>
After saving a task, you will be asked if you want to do a dry-run.
Doing a dry run allows you to test if your task works properly without saving or notifying about any ads.

<h4>Cron<h4>
When you are finished testing, you can prime your task to cache the first
round of ads to prevent a large spam of hits on your notitication agent.
By default, you will receive the 3 most recent ads in the priming.
Any future runs of your task will send notifications as normal.

When priming is done you will be asked if you want to create a cron
job for your task. 

This will use the frequency of the task you set previously.
Any new tasks made with the same frequency will use the same cron job and
any new tasks new tasks with a different frequency will create a new cron
job. If there all jobs with the same frequency are deleted, the cronjob matching
that frequency will also be deleted

<h3>Commands<h3>
See ./main.py --help for all available tasks
