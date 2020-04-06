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

Install git if it is not already installed.

>$ sudo apt install git

Use git to pull the repository files to your machine, use a directory your which user has write permissions for.
In this case we will use the home directory.
>$ cd ~

>$ sudo git clone https://github.com/suppaduppax/Scraper-Discord-Notification.git

Install some required packages:
>$ sudo apt install python3-pip python3-bs4

Install some required packages for python:
>$ sudo -H pip3 install -r ~/Scraper-Discord-Notification/requirements.txt

<h2>Setup</h2>

Give main.py executable permissions.
>$ sudo chmod +x ~/Scraper-Discord-Notification/main.py

Make sure you have a crontab for you user
>$ crontab -l

If the output shows ```$ no crontab for <user>``` then create a new crontab for the user
>$ crontab -e

Select an editor and save with **CTRL + S** then **CTRL +X** to exit.

Try your crontab again
>$ crontab -l

```
# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
# 
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
# 
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
# 
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
# 
# For more information see the manual pages of crontab(5) and cron(8)
# 
# m h  dom mon dow   command
```
If you have a similar output, your user should now have a crontab

**Get a Discord Webhook**

You will need a webhook when making your notification agent, get this ready.
Check out: https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks

**Get a search URL**

You will need this when making a source, get this ready as well.
To get a search URL, go to http://www.kijiji.ca and use the search box for the item you're looking for.

![Kijiji - Search](https://user-images.githubusercontent.com/58180427/69773229-dd3fe300-1157-11ea-884c-5f5c12b3f874.png)

Use any of the filters on the left hand side of the page to narrow down your search as closely as you want (e.g. regions, price, etc.).

![Kijiji - URL](https://user-images.githubusercontent.com/58180427/69773238-e16c0080-1157-11ea-8105-797037bb5687.png)

**Add a Notification Agent**

>$ python3 ~/Scraper-Discord-Notification/main.py notification-agent add

Notification agents are what will be used to notify you when new ads are found.
Right now, only discord is supported more will he more added in the future.
 
**Add a Source**
>$ python3 ~/Scraper-Discord-Notification/main.py source add
 
Sources contain the configuration that will be used when doing the actual scraping. Right
now only the kijiji module is supported but more will be added in the future.

**Add a Task**
>$ python3 ~/Scraper-Discord-Notification/main.py task add
 
Tasks are what executes the scraping process and runs the notification.
You can set the frequency of these tasks which will use cron to run them on
a schedule.

<h2>Dry-runs and Priming</h2>
After saving a task, you will be asked if you want to do a dry-run.
Doing a dry run allows you to test if your task works properly without saving or notifying about any ads.

When you are finished testing, you can prime your task to cache the first
round of ads to prevent a large spam of hits on your notitication agent.
By default, you will receive the 3 most recent ads in the priming.
Any future runs of your task will send notifications as normal.

<h2>Cron</h2>
At the very end of task creation you will be asked if you want to create a cron
job for your task. 

This will use the frequency of the task you set previously.
Any new tasks made with the same frequency will use the same cron job and
any new tasks new tasks with a different frequency will create a new cron
job. If there all jobs with the same frequency are deleted, the cronjob matching
that frequency will also be deleted

<h2>Settings</h2>
There is only a couple of implemented settings in the 'settings.yaml' file.

```log_rotation_files - the number of files to rotate in logs/```

```recent_ads - the number of ads to notify about when running a task. 0 disables this and will show an infinite number of ads```

<h2>Commands</h2>
Use the help command to see what commands are available
>$ python3 main.py --help 
