#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, curses, sys, sqlite3


def sanitize(_input):
	if type(_input) in [int]:
		return _input
	else:
		return _input.replace("'", "<single_quote>")

def desanitize(_input):
	if type(_input) in [int]:
		return _input
	else:
		return _input.replace("<single_quote>", "'")

class Host:
	_id = 0
	ip = ""
	name = ""
	ports = []
	descriptions = []
	def __init__(self, row=""):
		if row !="":
			self._id = desanitize(row[0])
			self.ip = desanitize(row[1])
			self.name = desanitize(row[2])

class Port:
	_id = 0
	_host_id = 0
	port_number = 0
	protocol = ""
	service = ""
	descriptions = []
	def __init__(self, row=""):
		if row !="":
			self._id = desanitize(row[0])
			self._host_id = desanitize(row[1])
			self.port_number = desanitize(row[2])
			self.protocol = desanitize(row[3])
			self.service = desanitize(row[4])
class Description:
	_id = 0
	_port_id = 0
	_host_id = 0
	description = ""
	def __init__(self, row=""):
		if row !="":	
			self._id = desanitize(row[0])
			self._port_id = desanitize(row[1])
			self._host_id = desanitize(row[2])
			self.description = desanitize(row[3])
		
#-------------------------------------

class SQLITE:
	dbname = ""

	def __execute_query(self, queries=[]):
		if queries is None or not isinstance(queries, list) or len(queries) == 0:
			return None
		
		# Conexión a la base de datos
		conn = sqlite3.connect(self.dbname)
		cursor = conn.cursor()
		results = []

		for query in queries:
			cursor.execute(query)
		results = cursor.fetchall()

		conn.commit()

		conn.close()

		return results

	def __init__(self, dbname):
		# Nombre de la base de datos
		self.dbname = dbname

		queries = []
		queries.append('CREATE TABLE IF NOT EXISTS hosts ( _id INTEGER PRIMARY KEY AUTOINCREMENT, ip TEXT NOT NULL, name TEXT NOT NULL)')
		queries.append('CREATE TABLE IF NOT EXISTS ports ( _id INTEGER PRIMARY KEY AUTOINCREMENT, host_id INTEGER NOT NULL, port_number INTEGER NOT NULL, protocol TEXT NOT NULL, service TEXT NOT NULL, FOREIGN KEY (host_id) REFERENCES host (_id))')
		queries.append('CREATE TABLE IF NOT EXISTS descriptions ( _id INTEGER PRIMARY KEY AUTOINCREMENT, port_id INTEGER NOT NULL, host_id INTEGER NOT NULL, description TEXT, FOREIGN KEY (port_id) REFERENCES port (_id), FOREIGN KEY (host_id) REFERENCES host (_id))')

		self.__execute_query(queries)

	def delete_description_by_id(self, description_id):

		self.__execute_query([f"DELETE FROM descriptions WHERE _id='{sanitize(description_id)}'"])

	def delete_port_by_id(self, port_id):
		self.__execute_query([f"DELETE FROM ports WHERE _id='{sanitize(port_id)}'"])
		self.__execute_query([f"DELETE FROM descriptions WHERE port_id='{sanitize(port_id)}'"])

	def delete_host_by_id(self, host_id):
		self.__execute_query([f"DELETE FROM hosts WHERE _id='{sanitize(host_id)}'"])
		self.__execute_query([f"DELETE FROM ports WHERE host_id='{sanitize(host_id)}'"])
		self.__execute_query([f"DELETE FROM descriptions WHERE host_id='{sanitize(host_id)}'"])

	def delete_description(self, description):
		self.__execute_query([f"DELETE FROM descriptions WHERE description='{sanitize(description.description)}' AND host_id='{sanitize(description._host_id)}' AND port_id='{sanitize(description._port_id)}'"])

	def delete_port(self, port):
		self.__execute_query([f"DELETE FROM ports WHERE port_number='{sanitize(port.port_number)}' AND host_id='{sanitize(port._host_id)}'"])
		self.__execute_query([f"DELETE FROM descriptions WHERE host_id='{sanitize(port._host_id)}' AND port_id='{sanitize(port._id)}'"])

	def delete_host(self, host):
		self.__execute_query([f"DELETE FROM hosts WHERE ip='{sanitize(host.ip)}'"])
		self.__execute_query([f"DELETE FROM ports WHERE host_id='{sanitize(port._host_id)}'"])
		self.__execute_query([f"DELETE FROM descriptions WHERE host_id='{sanitize(port._host_id)}'"])

	def update_description_by_id(self, description):
		self.__execute_query([f"UPDATE descriptions SET description='{sanitize(description.description)}' WHERE _id={sanitize(description._id)}"])

	def update_port_by_id(self, port):
		self.__execute_query([f"UPDATE ports SET protocol='{sanitize(port.protocol)}', service='{sanitize(port.service)}', port_number='{sanitize(port.port_number)}' WHERE _id={sanitize(port._id)}"])

	def update_host_by_id(self, host):
		self.__execute_query([f"UPDATE hosts SET name='{sanitize(host.name)}', ip='{sanitize(host.ip)}' WHERE _id={sanitize(host._id)}"])

	def update_description(self, description):
		d = self.__execute_query([f"SELECT * FROM descriptions WHERE description='{sanitize(description.description)}' AND host_id='{sanitize(description._host_id)}' AND port_id='{sanitize(description._port_id)}'"])
		if d == None:
			return

		if len(d) == 0:
			self.__execute_query([f"INSERT INTO descriptions(port_id,host_id,description) VALUES ('{sanitize(description._port_id)}','{sanitize(description._host_id)}','{sanitize(description.description)}')"])

		d = self.__execute_query([f"SELECT * FROM descriptions WHERE description='{sanitize(description.description)}' AND host_id='{sanitize(description._host_id)}' AND port_id='{sanitize(description._port_id)}'"])[0]

		return Description(d)

	def update_port(self, port):
		p = self.__execute_query([f"SELECT * FROM ports WHERE port_number='{sanitize(port.port_number)}' AND host_id='{sanitize(port._host_id)}'"])
		if p == None:
			return

		if len(p) == 0:
			self.__execute_query([f"INSERT INTO ports(host_id,port_number,protocol,service) VALUES ('{sanitize(port._host_id)}','{sanitize(port.port_number)}','{sanitize(port.protocol)}','{sanitize(port.service)}')"])
		else:
			self.__execute_query([f"UPDATE ports SET protocol='{sanitize(port.protocol)}', service='{sanitize(port.service)}' WHERE port_number='{sanitize(port.port_number)}' AND host_id='{sanitize(port._host_id)}'"])

		p = self.__execute_query([f"SELECT * FROM ports WHERE port_number='{sanitize(port.port_number)}' AND host_id='{sanitize(port._host_id)}'"])[0]

		return Port(p)


	def update_host(self, host):
		h = self.__execute_query([f"SELECT * FROM hosts WHERE ip='{sanitize(host.ip)}'"])
		if h == None:
			return

		if len(h) == 0:
			self.__execute_query([f"INSERT INTO hosts(ip,name) VALUES ('{sanitize(host.ip)}','{sanitize(host.name)}')"])
		else:
			self.__execute_query([f"UPDATE hosts SET name='{sanitize(host.name)}' WHERE ip='{sanitize(host.ip)}'"])

		h = self.__execute_query([f"SELECT * FROM hosts WHERE ip='{sanitize(host.ip)}'"])[0]

		return Host(h)


	def get_hosts(self):
		hs = self.__execute_query(["SELECT * FROM hosts"])
		if hs == None:
			return
		hosts = []
		for h in hs:
			hosts.append(Host(h))

		for host in hosts:
			host.ports = []
			host.descriptions = []

			for d in self.__execute_query([f"SELECT * FROM descriptions WHERE host_id='{host._id}' AND port_id=0"]):
				host.descriptions.append(Description(d))

			for p in self.__execute_query([f"SELECT * FROM ports WHERE host_id='{host._id}'"]):
				host.ports.append(Port(p))
				
			for port in host.ports:
				port.descriptions = []
				for d in self.__execute_query([f"SELECT * FROM descriptions WHERE host_id='{host._id}' AND port_id='{port._id}'"]):
					port.descriptions.append(Description(d))

		return hosts

#-------------------------------------

COLOR_BLACK = 1
COLOR_GREEN = 2
COLOR_YELLOW = 3
COLOR_BLUE = 4
COLOR_MAGENTA = 5
COLOR_CYAN = 6
COLOR_WHITE = 7
COLOR_RED = 8
COLOR_ORANGE = 9

sqlite = None


def gui_host(stdscr, menu, current_row):
	host = Host()
	if len(menu) > 0:
		host._id = int(menu[current_row].split("-")[0].split(",")[0])

	stdscr.clear()
	stdscr.addstr(0, 0, "Host IP:", curses.color_pair(COLOR_GREEN))
	stdscr.refresh()
	curses.echo()  # Muestra la entrada del usuario
	host.ip = stdscr.getstr(0, len("Host IP:")+1).decode(encoding="utf-8")
	curses.noecho()  # Oculta la entrada del usuario

	stdscr.addstr(1, 0, "Host name:", curses.color_pair(COLOR_GREEN))
	stdscr.refresh()
	curses.echo()  # Muestra la entrada del usuario
	host.name = stdscr.getstr(1, len("Host name:")+1).decode(encoding="utf-8")
	curses.noecho()  # Oculta la entrada del usuario

	stdscr.clear()
	return host

def gui_port(stdscr, menu, current_row):
	port = Port()
	if len(menu) > 0:
		port._host_id = int(menu[current_row].split("-")[0].split(",")[0])
		port._id = int(menu[current_row].split("-")[0].split(",")[1])

	stdscr.clear()
	stdscr.addstr(0, 0, "Port number:", curses.color_pair(COLOR_GREEN))
	stdscr.refresh()
	curses.echo()  # Muestra la entrada del usuario
	port.port_number = stdscr.getstr(0, len("Port number:")+1).decode(encoding="utf-8")
	curses.noecho()  # Oculta la entrada del usuario

	stdscr.addstr(1, 0, "Protocol (UDP/TCP):", curses.color_pair(COLOR_GREEN))
	stdscr.refresh()
	curses.echo()  # Muestra la entrada del usuario
	port.protocol = stdscr.getstr(1, len("Protocol (UDP/TCP):")+1).decode(encoding="utf-8").upper()
	curses.noecho()  # Oculta la entrada del usuario

	stdscr.addstr(2, 0, "Service:", curses.color_pair(COLOR_GREEN))
	stdscr.refresh()
	curses.echo()  # Muestra la entrada del usuario
	port.service = stdscr.getstr(2, len("Service:")+1).decode(encoding="utf-8")
	curses.noecho()  # Oculta la entrada del usuario
	stdscr.clear()

	return port

def gui_description(stdscr, menu, current_row):
	description = Description()
	if len(menu) > 0:
		description._host_id = int(menu[current_row].split("-")[0].split(",")[0])
		description._port_id = int(menu[current_row].split("-")[0].split(",")[1])
		description._id = int(menu[current_row].split("-")[0].split(",")[2])

	stdscr.clear()
	stdscr.addstr(0, 0, "Description:", curses.color_pair(COLOR_GREEN))
	stdscr.refresh()
	curses.echo()  # Muestra la entrada del usuario
	description.description = stdscr.getstr(0, len("Description:")+1).decode(encoding="utf-8")
	curses.noecho()  # Oculta la entrada del usuario
	stdscr.clear()
	return description

def curse(stdscr):
	# Ocultar el cursor
	curses.curs_set(0)
	# Configurar colores
	curses.start_color()
	curses.init_pair(COLOR_BLACK, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(COLOR_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(COLOR_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(COLOR_BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
	curses.init_pair(COLOR_MAGENTA, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	curses.init_pair(COLOR_CYAN, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(COLOR_RED, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(COLOR_ORANGE, 208, curses.COLOR_BLACK)
	
	current_row = 0

	height, width = stdscr.getmaxyx()
	x_min = 0
	x_max = height

	while True:
		menu = []
		hosts = sqlite.get_hosts()
		for host in hosts:
			menu.append(f"{host._id},0,0-{host.ip},{host.name}")
			
			for description in host.descriptions:
				menu.append(f"{description._host_id},{description._port_id},{description._id}-{description.description}")
			for port in host.ports:
				menu.append(f"{port._host_id},{port._id},0-{port.protocol}/{port.port_number},{port.service}")
				for description in port.descriptions:
					menu.append(f"{description._host_id},{description._port_id},{description._id}-{description.description}")

		stdscr.clear()

		#Leyenda
		header="Exit (q, ESC), New Host (h), New Port (p), New Desc (d), Modify(Ins), Remove (Del),"
		stdscr.addstr(0, (width - len(header)) // 2, header, curses.color_pair(1))
		stdscr.addstr(1, 0, "-"*width, curses.color_pair(0))

		if len(menu) < height-2:
			x_max = x_min+len(menu)
		else:
			x_max = x_min+height-2
		
		actual_menu = menu[x_min:x_max]

		for idx, row in enumerate(actual_menu):
			x = 5  # Margen izquierdo
			y = idx + 2  # Comenzar desde la primera fila
			
			is_next_port = False
			is_next_desc = False
			if len(actual_menu) <= idx-1:
				if int(actual_menu[idx+1].split("-")[0].split(",")[1]) != 0:
					is_port = True
				if int(actual_menu[idx+1].split("-")[0].split(",")[2]) != 0:
					is_desc = True

			is_port = False
			is_desc = False
			if int(row.split("-")[0].split(",")[1]) != 0:
				is_port = True
			if int(row.split("-")[0].split(",")[2]) != 0:
				is_desc = True

			row = row.split("-")[1]
			
			#Cursor
			if idx == current_row:
				stdscr.attron(curses.color_pair(1))
				stdscr.addstr(y, 2, " > ")
				stdscr.attroff(curses.color_pair(1))

			#Flechas superior e inferior
			if x_min > 0:
				stdscr.addstr(2, 0, "↑")
			if len(actual_menu)+2 >= height and len(menu)>x_max:
				stdscr.addstr(height-1, 0, "↓")

			if not is_port and not is_desc:
				stdscr.addstr(y, x, "-")
				stdscr.addstr(y, x+2, row.split(",")[0], curses.color_pair(COLOR_RED) | curses.A_BOLD)
				if len(row.split(",")[1]) > 0:
					stdscr.addstr(y, x+2+len(row.split(",")[0])+1, "-")
					stdscr.addstr(y, x+2+len(row.split(",")[0])+1+2, row.split(",")[1], curses.color_pair(COLOR_ORANGE))
			elif is_port and not is_desc:
				stdscr.addstr(y, x+3, "├")
				if "TCP" in row.split(",")[0]:
					stdscr.addstr(y, x+3+3, row.split(",")[0], curses.color_pair(COLOR_YELLOW) | curses.A_BOLD)
				elif "UDP" in row.split(",")[0]:
					stdscr.addstr(y, x+3+3, row.split(",")[0], curses.color_pair(COLOR_BLUE) | curses.A_BOLD)
				else:
					stdscr.addstr(y, x+3+2, row.split(",")[0], curses.color_pair(COLOR_CYAN) | curses.A_BOLD)
				stdscr.addstr(y, x+3+2+len(row.split(",")[0])+2, "-")
				stdscr.addstr(y, x+3+2+len(row.split(",")[0])+2+2, row.split(",")[1], curses.color_pair(COLOR_CYAN))
			elif not is_port and is_desc:
				stdscr.addstr(y, x+3, "├")
				stdscr.addstr(y, x+3+3, "[i]", curses.color_pair(COLOR_GREEN))
				stdscr.addstr(y, x+3+3+len("[i]")+1, row.split(",")[0])
			elif is_port and is_desc:
				stdscr.addstr(y, x+3, "│")
				stdscr.addstr(y, x+7, "├")
				stdscr.addstr(y, x+7+3, "[i]", curses.color_pair(COLOR_GREEN))
				stdscr.addstr(y, x+7+3+len("[i]")+1, row.split(",")[0])

		stdscr.refresh()

		key = stdscr.getch()

		if key == curses.KEY_UP:
			if current_row > 0:
				current_row -= 1
			else:
				if x_min > 0:
					x_min-=1

		elif key == curses.KEY_DOWN:
			if current_row < len(actual_menu) - 1:
				current_row += 1
			else:
				if len(actual_menu)+2 == height and len(menu)>x_max:
					x_min+=1

		elif key == curses.KEY_LEFT:
			pass
		elif key == ord('h'):
			sqlite.update_host(gui_host(stdscr, actual_menu, current_row))
		elif key == ord('p'):
			if len(actual_menu) > 0:
				sqlite.update_port(gui_port(stdscr, actual_menu, current_row))
		elif key == ord('d'):
			if len(actual_menu) > 0:
				sqlite.update_description(gui_description(stdscr, actual_menu, current_row))
		elif key == curses.KEY_DC:	#modify
			if len(actual_menu) > 0:
				if int(actual_menu[current_row].split("-")[0].split(",")[2]) != 0:
					sqlite.delete_description_by_id(int(actual_menu[current_row].split("-")[0].split(",")[2]))
				else:
					if int(actual_menu[current_row].split("-")[0].split(",")[1]) != 0:
						sqlite.delete_port_by_id(int(actual_menu[current_row].split("-")[0].split(",")[1]))
					elif int(actual_menu[current_row].split("-")[0].split(",")[0]) != 0:
						sqlite.delete_host_by_id(int(actual_menu[current_row].split("-")[0].split(",")[0]))

				current_row -= 1
		elif key in [curses.KEY_IC, ord('m')] :	#modify
			if len(actual_menu) > 0:
				if int(actual_menu[current_row].split("-")[0].split(",")[2]) != 0:
					sqlite.update_description(gui_description(stdscr, actual_menu, current_row))
				else:
					if int(actual_menu[current_row].split("-")[0].split(",")[1]) != 0:
						sqlite.update_port(gui_port(stdscr, actual_menu, current_row))
					elif int(actual_menu[current_row].split("-")[0].split(",")[0]) != 0:
						sqlite.update_host_by_id(gui_host(stdscr, actual_menu, current_row))

		elif key == 27 or key == ord('q'):  # Tecla "Esc"
			break


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Host and findings manager based in sqlite')
	parser.add_argument('-DB', required=True, help="Database name and location")
	args = parser.parse_args()

	sqlite = SQLITE(args.DB)
	curses.set_escdelay(25)
	curses.wrapper(curse)
