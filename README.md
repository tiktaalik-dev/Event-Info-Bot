# Event Info Bot
> Bot for instant messaging platforms. On a first stage it only works with Telegram and Twitter platforms.
It's intended for replying to user queries automatically, providing the date when an event is due as well as 
calculating how many years, months, days, hours, minutes or seconds are left from today to the event date.

[![Python Version][python-image]][python-url]
[![GAE compatibility][gae-image]][gae-url]
[![Download from][bot-downloads-image]][bot-downloads-url]
[![Download from][bot-github-downloads-image]][bot-github-downloads-url]

Use this application to manage Telegram and Twitter accounts that inform your users about the date when an event is due. 

This application is able to both send periodic reminders in Twitter, as well as replying to user queries, calculating 
the time and date difference since today.


## Installation

Simply download the bot code, copy it to your project directory, customise it, and then deploy it to your production server. In case 
you deploy to the Google App Engine platform, please follow the quickstart instructions provided by 
[Google](https://cloud.google.com/appengine/docs/standard/python3/quickstart)

## Development setup

Create a virtual environment for Python 3.7 and install the 
required libraries using the requirements.txt file.

```sh
cd my-bot-project/
virtualenv --python=python3.7 venvs/venv3.7
pip install -t requirements.txt
```

If you're using the Google App Engine platform to deploy your bot (required for Twitter bot), then you must also 
install the Cloud SDK and set up a Google Cloud Platform project for App Engine. You can read about it in 
[GCP's Quickstart documentation](https://cloud.google.com/appengine/docs/standard/python3/quickstart)

## Configuration

First, you should edit the /bot/app/config.py file to customise your bot by adjusting the proper settings.

Secondly, make a copy of /cron-example.yaml and name it /cron.yaml as that's the name used by Google App Engine. Customise it 
for your timezone and the schedule that would work better for your bot. Of course, if you won't deploy your application 
to GAE then you can skip this step.

Next, check the README file in the /SSL-certs folder for important information regarding using SSL certificates and 
private keys with your Telegram bot.

Then read the docstring in the /bot/app/secrets.py file to learn how to fill in your secret tokens.

Last but not least, check the /bot/app/views/l10n.py (localisation) file to see the languages available, make a note of 
the language code so you can enter it in appropriate setting of the config.py file. Also, feel free add a translation 
in case your language is not yet available.

## Release History

* 0.9.5 Updated README file
* 0.9.4 Bug fix
* 0.9.3 Bug fix
* 0.9.2 Bug fix
* 0.9.1 Bug fix
* 0.9.0
    * The first proper release
    * Bot features Telegram messenger and Twitter platform functionality
    * Code is completely documented
    * Work in progress: implementing unit testing in version 1.0

## About the author

Rodrigo Gambra – [@DoctorToffu](https://twitter.com/DoctorToffu) – rodrigo@tiktaalik.dev

Distributed under the GPL v.3 license. See ``LICENSE`` for more information.

     Event Info Bot - Bot service software for Telegram and Twitter to provide user with
                      reminders of event date and info on request
    
     Copyright (C) 2019 Tiktaalik (Rodrigo Gambra-Middleton)
                        Address your enquiries to: info@tiktaalik.dev

     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program.  If not, see <https://www.gnu.org/licenses/>.


[https://bitbucket.org/rgambra/event-info-bot/](https://bitbucket.org/rgambra/event-info-bot/)

## Contributing

1. Fork it (<https://bitbucket.org/rgambra/event-info-bot/>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
6. You may also contribute to write the [Wiki][wiki]

## Acknowledgements

1. The [python-telegram-bot library](https://github.com/python-telegram-bot/python-telegram-bot).
 Definitely, "a wrapper you can't refuse" :-)
2. The [Tweepy library](https://github.com/tweepy/tweepy). A really pleasant library to work with!
3. Dan Bader for providing a free README.md template for this documentation. 
See [https://dbader.org/blog/write-a-great-readme-for-your-github-project]

<!-- Markdown link & img dfn's -->
[python-image]: https://img.shields.io/badge/python-3.7-blue
[python-url]: https://www.python.org/downloads/release/python-370/
[gae-image]: https://img.shields.io/badge/Google%20App%20Engine-Python%203%20(standard)-brightgreen
[gae-url]: https://cloud.google.com/appengine/docs/standard/python3/runtime
[bot-downloads-image]: https://img.shields.io/badge/Download%20from-BitBucket-orange
[bot-github-downloads-image]: https://img.shields.io/badge/Download%20from-GitHub-orange
[bot-downloads-url]: https://bitbucket.org/rgambra/event-info-bot/downloads/?tab=downloads
[bot-github-downloads-url]: https://github.com/doctortoffu/Event-Info-Bot
[wiki]: https://bitbucket.org/rgambra/event-info-bot/wiki/
