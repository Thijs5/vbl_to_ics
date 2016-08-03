import json, requests, os, sys
from datetime import datetime, timedelta

def get_json_for_team_id(team_id):
	print('looking up team')
	url = 'http://vblcb.wisseq.eu/VBLCB_WebService/data/TeamMatchesByGuid?teamGuid={0}'.format(team_id)
	return requests.get(url = url).json()

def get_json_for_game_guid(guid):
	url = 'http://vblcb.wisseq.eu/VBLCB_WebService/data/MatchesByWedGuid?issguid={0}'.format(guid)
	return requests.get(url = url).json()[0]['doc']

def map_json_to_game(game_as_json):
	return {
		'id': game_as_json['wedID'],
		'home_team': game_as_json['teamThuisNaam'],
		'visitors': game_as_json['teamUitNaam'],
		'datetime': datetime.strptime(game_as_json['datumString'] + game_as_json['beginTijd'], 
			'%d-%m-%Y%H.%M'),
		'accomodation': {
			'name': game_as_json['accommodatieDoc']['naam'],
			'address': {
				'street': game_as_json['accommodatieDoc']['adres']['straat'],
				'nr': game_as_json['accommodatieDoc']['adres']['huisNr'],
				'nr_addition': game_as_json['accommodatieDoc']['adres']['huisNrToev'],
				'postal_code': game_as_json['accommodatieDoc']['adres']['postcode'],
				'city': game_as_json['accommodatieDoc']['adres']['plaats'],
				'country': game_as_json['accommodatieDoc']['adres']['land']
			},
		'phone': game_as_json['accommodatieDoc']['telefoon'],
		'website': game_as_json['accommodatieDoc']['website']
		}
	}

def get_games_by_guid(guids):
	print('loading games for the season')
	games = []
	for guid in guids:
		data = get_json_for_game_guid(guid)
		game = map_json_to_game(data)
		games.append(game)
	return games

def write_line(file, txt):
	file.write(txt + '\n')

def write_ical_headers(file):
	write_line(file, 'BEGIN:VCALENDAR')
	write_line(file, 'VERSION:2.0')
	# write_line(file, 'PRODID:-//hacksw/handcal//NONSGML v1.0//EN')
	write_line(file, 'PRODID:-//hacksw/handcal//NONSGML v1.0//EN')

def write_ical_footer(file):
	write_line(file, 'END:VCALENDAR')

def utc_string(date):
	return date.isoformat().replace('-', '').replace(':', '')

def write_game_as_event(file, game):
	write_line(file, 'BEGIN:VEVENT')

	write_line(file, 'UID:{0}'.format(game['id']))
	write_line(file, 'SUMMARY:{0} - {1}'.format(game['home_team'], game['visitors']))
	write_line(file, 'DTSTAMP:{0}'.format(utc_string(game['datetime'])))
	write_line(file, 'DTSTART:{0}'.format(utc_string(game['datetime'])))
	write_line(file, 'DTEND:{0}'.format(utc_string(game['datetime'] + timedelta(hours=2))))
	write_line(file, 'LOCATION:{0} {1} {2} {3} {4}, {5}'
		.format(
			game['accomodation']['address']['street'] or '', 
			game['accomodation']['address']['nr'] or '', 
			game['accomodation']['address']['nr_addition'] or '', 
			game['accomodation']['address']['postal_code'] or '', 
			game['accomodation']['address']['city'] or '', 
			game['accomodation']['address']['country'] or ''))
	write_line(file, 'DESCRIPTION: Wedstrijdnummer: {0}\nSporthal: {1}'.format(game['id'], game['accomodation']['name']))

	write_line(file, 'END:VEVENT')

def write_games_to_ical_file(games):
	file_name = 'export.ics'

	if(os.path.exists(file_name)):
		print('deleting previous file')
		os.remove(file_name)

	print 'exporting to {0}'.format(file_name)
	with open(file_name, 'w') as file:
		write_ical_headers(file)
		for game in games:
			write_game_as_event(file, game)
		write_ical_footer(file)

def create_ical_for(team_id):
	team_data = get_json_for_team_id(team_id.replace(" ", "+"))
	games = get_games_by_guid([d['guid'] for d in team_data])
	write_games_to_ical_file(games)


if (__name__ == "__main__"):
	create_ical_for(sys.argv[1])