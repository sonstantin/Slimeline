#pylint:disable=W0611
#pylint:disable=W0612
import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox, filedialog
import json
from PIL import Image, ImageTk
import requests
import sys, os, pyperclip
from datetime import datetime



try:


    class Netzplaner:
        def __init__(self, master):
            print("============Slimeline============")
            image_url = "https://static.wikia.nocookie.net/minecraft_de_gamepedia/images/c/cc/Schleim.png/revision/latest/scale-to-width-down/150?cb=20200403150614.png"
            response = requests.get(image_url)
            with open("schleim.png", "wb") as f:
                f.write(response.content)
            
            
            self.master = master
            self.master.title("Slimeline 2.3")
            self.image = Image.open("schleim.png")
            self.image = ImageTk.PhotoImage(self.image)
            self.master.iconphoto(True, self.image)
            self.master.bell()
            
            self.canvasBG = "white"
            self.RouteFinder = False
            
            self.canvas = tk.Canvas(self.master, bg=self.canvasBG, width=600, height=400)
            self.canvas.pack(expand=True, fill=tk.BOTH)
            
            self.build_line = tk.Frame(self.master, relief="solid", borderwidth=5)
            self.build_line.pack(fill = tk.X)
            self.station_radius = 10

            self.bau = {}
            try:
                with open("Linewidth.json", mode="r", encoding="utf-8") as f:
                    self.width = json.load(f)
                    language = self.width[1]
                    self.doEnglish = self.width[2]
                    self.width = self.width[0]
            except FileNotFoundError:
                self.width = 7
                language = "Englisch"
                self.doEnglish = True
            except TypeError:
                self.width = 7
                language = "Englisch"
                with open("linewidth.json", mode="w", encoding="utf-8") as f:
                    json.dump(f)
            
            with open(f"slimeline_text_{language}.json", mode="r", encoding="utf-8") as f:
                self.strings = json.load(f)
                print(self.strings)
            print(self.strings["Slimeline wird geladen"])
            self.search = ""
            self.add_intermediate_stop_button = tk.Button(self.build_line, text=self.strings["Umsteigemöglichkeit hinzufügen"], command=self.add_intermediate_stop_prompt)
            self.add_intermediate_stop_button.pack()
            self.stations = {}
            self.lines = []
            self.current_line = []
            self.build_mode = True

            self.entry = tk.Entry(self.build_line)
            self.entry.pack(side=tk.TOP, fill=tk.X)

            self.canvas.bind("<Button-1>", lambda event: self.add_station(event, komplex=False))
            jetzt = datetime.now()
            self.uhrzeit = jetzt.strftime("%H : %M")  # Nur die Uhrzeit
            
            
            timeframe = tk.Frame(self.master, relief="solid", borderwidth=4)
            timeframe.place(x=0, y=0)
            self.time_Label = tk.Label(timeframe, text=self.uhrzeit, bg="white")
            self.time_Label.pack()
            self.create_line_button = tk.Button(self.build_line, text=self.strings["Linie erstellen"], command=self.create_line)
            self.create_line_button.pack()
            self.listbutton = tk.Button(self.master, text=self.strings["Liste der Stationen und Verbindungen"], command=self.lists)
            self.listbutton.pack()
            self.choose_color_button = tk.Button(self.master, text=self.strings["Linienfarbe wählen"], command=self.choose_color)
            self.choose_color_button.pack()

            # NEU: Separate Buttons für Speichern und Laden
            self.save_button = tk.Button(self.master, text=self.strings["Speichern/Laden"], command=self.saveOrLoad)
            self.save_button.pack()
            
            
            self.build_mode_button = tk.Button(self.master, text=self.strings["Bau-Modus deaktivieren"], command=self.toggle_build_mode)
            self.build_mode_button.pack()
            
            options = tk.Button(self.master, text=self.strings["Optionen"], command=lambda language=language: self.options(language=language))
            options.pack(anchor="w")

            self.line_color = "green"
            
            self.arrow = tk.Frame(self.master, relief="solid", borderwidth=5)
            self.arrow.pack(side=tk.RIGHT)
            
            self.up_button = tk.Button(self.arrow, text="↑", command=lambda: self.move_canvas(0, -1))
            self.up_button.pack(side=tk.RIGHT)
            self.down_button = tk.Button(self.arrow, text="↓", command=lambda: self.move_canvas(0, 1))
            self.down_button.pack(side=tk.RIGHT)
            self.left_button = tk.Button(self.arrow, text="←", command=lambda: self.move_canvas(-1, 0))
            self.left_button.pack(side=tk.RIGHT)
            self.right_button = tk.Button(self.arrow, text="→", command=lambda: self.move_canvas(1, 0))
            self.right_button.pack(side=tk.RIGHT)
            
            self.WASD = False

            self.routebutton = tk.Button(self.master, text=self.strings["Routenplaner öffnen"], command=lambda start="", stop="": self.open_route_planner_window(start="", stop=""))
            self.routebutton.pack(side=tk.LEFT)

            self.master.bind("<Up>", lambda event: self.move_canvas(0, -1))
            self.master.bind("<Down>", lambda event: self.move_canvas(0, 1))
            self.master.bind("<Left>", lambda event: self.move_canvas(-1, 0))
            self.master.bind("<Right>", lambda event: self.move_canvas(1, 0))
            if self.WASD:

                self.master.bind("<W>", lambda event: self.move_canvas(0, -1))
                self.master.bind("<A>", lambda event: self.move_canvas(-1, 0))
                self.master.bind("<S>", lambda event: self.move_canvas(0, 1))
                self.master.bind("<D>", lambda event: self.move_canvas(1, 0))
            
            print(self.strings["Das inizialisieren von Slimeline war erfolgreich!"])
            self.master.bind("<Escape>", self.exit)
            self.master.bind("<Control-s>", self.save_plan)
            self.master.bind("<Control-o>", self.load_plan)
            self.master.bind("<Shift-Return>", self.create_line)
            self.master.bind("<Shift-space>", self.showListOfAllStations)
            self.master.bind("<Control-space>", self.showListOfConnectionsToDelete)
            self.master.bind("<Control-u>", self.add_intermediate_stop_prompt)
            self.master.bind("<Alt-c>", self.choose_color)
            self.master.bind("<Control-b>", self.toggle_build_mode)
            self.master.bind("<Control-r>", lambda start="", stop="":self.open_route_planner_window(start="", stop=""))
            self.master.bind("<Control-k>", self.komplexlinecreation)
            self.master.bind("<Shift-Escape>", self.close_all_except_root)
            
            self.master.protocol("WM_DELETE_WINDOW", quit)
            self.update_clock()
            self.takt = {}
            
            
            




        

        
        
                    
        def update_clock(self):
            jetzt = datetime.now()
            hour = jetzt.hour
            minute = jetzt.minute
            second = jetzt.second
            self.uhrzeit = [hour, minute, second]  # Nur die Uhrzeit
            if self.doEnglish == True:
                if hour > 12:
                    hour = hour - 12
                    string = "PM"
                else:
                    string = "AM"
                self.uhrzeit = [hour, minute, second, string]
            self.time_Label.config(text=self.uhrzeit)
            self.master.after(1, self.update_clock)
        def close_all_except_root(self, event=None):
            # Alle Kinder von root durchgehen
            for widget in root.winfo_children():
                # Nur Toplevel-Fenster schließen (nicht das root selbst)
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
        def setOptions(self, canvasBG, uiBG, width):
            if canvasBG == "":
            
                canvasBG = colorchooser.askcolor(title=self.strings["Hintergrundfarbe wählen"])
                if uiBG[1]:
                    
                    self.canvas.configure(bg=f"{canvasBG[1]}")
                    self.canvas.configure(bg=f"{canvasBG[1]}")
                
            elif uiBG == "":
                uiBG = colorchooser.askcolor(title=self.strings["Hintergrundfarbe wählen"])
                if uiBG[1]:
                    self.uiBG = uiBG
                    self.master.configure(bg=f"{self.uiBG[1]}")
                    self.build_line.configure(bg=f"{self.uiBG[1]}")
                if uiBG == "black":
                            self.left_button.config(bg="black", fg="white")
            elif width == "":
                
                width = int(simpledialog.askinteger("Breite", self.strings["Wie breit sollen deine Linien sein? Die Aktuelle Breite beträgt"].replace("self.width", f"{self.width}")))
                if width is not None:
                
                    self.width = width
                    self.redraw()
                    self.draw_lines()
                    with open("Linewidth.json", mode="w", encoding="utf-8") as f:
                        json.dump(self.width, f)
            
            
            self.master.update()
        
            
            
            #self.build_line.configure(bg=f"{uiBG}")
        def exit(self, event=None):
            self.master.destroy()
            
        def set_language(self, language):
            self.width = [self.width, language, self.doEnglish]
            with open("Linewidth.json", mode="w", encoding="utf-8") as f:
                json.dump(self.width, f)
            python = sys.executable
            os.execl(python, python, *sys.argv)
        

        def options(self, language):
            settings = tk.Toplevel(self.master)
            settings.bind("<Shift-Escape>", self.close_all_except_root)
            
            settings.title(self.strings["Einstellungen"])
            graphical = tk.LabelFrame(settings, text=self.strings["Graphische Einstellungen"], relief="solid", borderwidth=5)
            graphical.grid(row=0, column=0)
            canvasbgEntry = tk.Button(graphical, text=self.strings["Bestimmen"], command=lambda uiBG="bla", canvasBG="", width="bla": self.setOptions(uiBG="bla", canvasBG="", width="bla"))
            canvasbgEntry.grid(row=0, column=1)
            canvasbgLabel = tk.Label(graphical, text=self.strings["Hintergrund des Plans bestimmen:"])
            
            
            canvasbgLabel.grid(row=0, column=0)
            
            uiLabel = tk.Label(graphical, text=self.strings["Hintergrundfarbe wählen"])
            uiLabel.grid(row=1, column=0)
            uiEntry = tk.Button(graphical, text=self.strings["Bestimmen"], command=lambda uiBG="", canvasBG="bla", width="bla": self.setOptions(uiBG="", canvasBG="bla", width="bla"))
            uiEntry.grid(row=1, column=1)
            
            widthLabel = tk.Label(graphical, text=self.strings["Breite der Linien bestimmen:"])
            widthLabel.grid(row=2, column=0)
            
            widthEntry = tk.Button(graphical, text=self.strings["Bestimmen"], command=lambda canvasBG="bla", uiBG="bla", width="": self.setOptions(canvasBG="bla", uiBG="bla", width=""))
            widthEntry.grid(row=2, column=1)

            lingual = tk.LabelFrame(settings, relief="solid", text=self.strings["Sprache"])
            lingual.grid(row=1, column=0)

            tk.Button(lingual, text="Deutsch", command=lambda language="Deutsch": self.set_language(language=language)).pack()
            tk.Button(lingual, text="English", command=lambda language="Englisch": self.set_language(language=language)).pack()
            tk.Button(lingual, text="Latinum", command=lambda language="Latein": self.set_language(language=language)).pack()
            temporal = tk.LabelFrame(settings, text=self.strings["Art der Zeit"], relief="solid", borderwidth=1)
            temporal.grid(row=2, column=0)
            self.changeType = tk.Button(temporal, text="1-24", command=lambda language=language: self.toggle_clock(language=language))
            self.changeType.pack()
            
        def toggle_clock(self, language):
            if self.doEnglish == False:
                self.doEnglish = True
                self.changeType.config(text="AM/PM")
                self.master.update()
            else:
                self.doEnglish = False
                self.changeType.config(text="1-24")
                self.master.update()
            
            with open("linewidth.json", mode="w", encoding="utf-8") as f:
                json.dump([self.width, language, self.doEnglish], f)
        def saveOrLoad(self):
            Auswahl = tk.Toplevel(self.master)
            Auswahl.title(self.strings["Auswahl zum Speichern oder Laden"])
            SaveButton = tk.Button(Auswahl, text=self.strings["Speichern"], command=self.save_plan)
            SaveButton.pack()
            LoadButton = tk.Button(Auswahl, text=self.strings["Laden"], command=self.load_plan)
            LoadButton.pack()
            Auswahl.bind("<Shift-Escape>", self.close_all_except_root)
            
        def open_route_planner_window(self, start, stop, event=None):
            window = tk.Toplevel(self.master)
            window.title(self.strings["Routenplaner"])
            window.bind("<Shift-Escape>", self.close_all_except_root)
            start_label = tk.Label(window, text=self.strings["Startstation:"])
            start_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            self.start_entry = tk.Entry(window)
            self.start_entry.grid(row=0, column=1, padx=10, pady=5)

            end_label = tk.Label(window, text=self.strings["Zielstation:"])
            end_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            self.end_entry = tk.Entry(window)
            self.end_entry.grid(row=1, column=1, padx=10, pady=5)
            self.start_entry.insert(0, start)
            self.end_entry.insert(0, stop)

            calculate_button = tk.Button(window, text=self.strings["Route berechnen"], command=self.calculate_route)
            calculate_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
            
        def lists(self):
            ask = tk.Toplevel(self.master)
            ask.title(self.strings["Listen"])
            ask.bind("<Shift-Escape>", self.close_all_except_root)
            OfStations = tk.Button(ask, text=self.strings["Liste aller Stationen zeigen"], command=self.showListOfAllStations)
            OfStations.pack()
            OfLines = tk.Button(ask, text=self.strings["Liste aller Verbindungen zeigen"], command=self.showListOfConnectionsToDelete)
            OfLines.pack()


        def calculate_wait_time(self, current_time, takt_in_seconds):
            
            if not isinstance(takt_in_seconds, int) or takt_in_seconds == 0:
                return 0  # Kein Takt vorhanden

            remainder = current_time % takt_in_seconds
            wait_time = takt_in_seconds - remainder if remainder != 0 else 0
            return wait_time
        def get_travel_time(self, from_station, to_station, line_name):
            for line_data in self.lines:
                if line_data[0][0] != line_name:
                    continue
                points, times = line_data[1], line_data[2]
                for i in range(len(points) - 1):
                    if (points[i][2] == from_station and points[i+1][2] == to_station) or \
                    (points[i+1][2] == from_station and points[i][2] == to_station):
                        t = times[i]
                        # ⬇ Convert safely to int
                        if isinstance(t, list) and t:
                            t = t[0]
                        return int(t)
            return 0


        def calculate_route(self):
            start_station = self.start_entry.get()
            end_station   = self.end_entry.get()

            if start_station not in self.stations:
                messagebox.showerror(self.strings["Fehler"],
                                    f"Die Startstation '{start_station}' existiert nicht.")
                return
            if end_station not in self.stations:
                messagebox.showerror(self.strings["Fehler"],
                                    f"Die Zielstation '{end_station}' existiert nicht.")
                return

            (distances, previous_stations,
            previous_lines, segment_times,
            wait_times) = self.dijkstra(start_station)    # <-- collect wait_times

            if distances[end_station] == float('inf'):
                messagebox.showinfo(self.strings["Fehler"],
                                    self.strings["Es gibt keine Verbindung zwischen den Stationen."])
                return

            # ---- Route rekonstruieren ----
            path, lines_used = [], []
            station = end_station
            while station:
                path.insert(0, station)
                lines_used.insert(0, previous_lines.get(station))
                station = previous_stations[station]

            times_used = [0]
            waits_used = [0]                               # <-- NEW
            for i in range(1, len(path)):
                times_used.append(segment_times.get(path[i], 0))
                waits_used.append(wait_times.get(path[i], 0))

            total_seconds = distances[end_station]
            minutes, seconds = divmod(total_seconds, 60)
            minuteLabel = self.strings["Minute"] if minutes == 1 else self.strings["Minuten"]
            secondLabel = self.strings["Sekunde"] if seconds == 1 else self.strings["Sekunden"]

            # --- total waiting time across the route ---
            total_wait = sum(waits_used)
            wait_min, wait_sec = divmod(total_wait, 60)

            # ---- GUI ----
            route_window = tk.Toplevel(self.master)
            route_window.title(f"{self.strings['Kürzeste Route von']} {start_station} {self.strings['nach']} {end_station}")

            title = tk.Label(
                route_window,
                text=(
                    f"{self.strings['Kürzeste Route von']} {start_station} {self.strings['nach']} {end_station} "#hier
                    
                ),
                font=("Arial", 12, "bold")
            )
            title.pack(pady=10)

            # show total platform waiting time
            wait_label = tk.Label(
                route_window,
                text=f"{self.strings['Gesamte Wartezeit auf Bahnsteigen']} {wait_min} min {wait_sec} s",
                font=("Arial", 11, "italic")
            )

            wait_label.pack(pady=5)
            Text = f"{self.strings['Zeit']}: "
            unitcount = 0
            for unit in self.uhrzeit:
                if unit == "AM" or unit == "PM":
                    Text += f" {str(unit)}"
                elif unitcount == 0:
                    Text += str(unit)
                    unitcount += 1
                else:
                    Text += f":{unit}"
                    unitcount += 1
            time_label = tk.Label(route_window,
                                  text=Text,
                                  font=("Arial", 11, "italic"))
            time_label.pack(pady=5)

            route_window.bind("<Shift-Escape>", self.close_all_except_root)

            container = tk.Frame(route_window)
            container.pack(padx=10, pady=5)
            distances, previous_stations, previous_lines, segment_times, wait_times = self.dijkstra(start_station)

            total_wait = sum(wait_times.values())
            print(f"Total platform wait time: {total_wait // 60} min {total_wait % 60} s")
            insgesamt_time = wait_min * 60 + wait_sec
            for i in range(len(path)):
                segment_frame = tk.Frame(container,
                                        bg="#f0f0f0" if i % 2 == 0 else "#ffffff",
                                        pady=5)
                segment_frame.pack(fill="x", padx=5, pady=1)

                text_parts = []
                if i > 0 and lines_used[i]:
                    line_name, color = lines_used[i]
                    text_parts.append(("→", "black"))
                    text_parts.append((f"[{line_name}", color))

                    duration = times_used[i]
                    travel_time = self.get_travel_time(path[i-1], path[i], line_name)
                    wait_time   = max(0, waits_used[i])        # <-- per-segment wait

                    parts = []
                    if travel_time:
                        parts.append(f"{travel_time // 60} min {travel_time % 60} s {self.strings['Fahrt']}")
                        insgesamt_time += travel_time
                        f"({minutes} {minuteLabel} und {seconds} {secondLabel})"

                    if wait_time:
                        parts.append(f"{wait_time // 60} min {wait_time % 60} s {self.strings['Warten']}")

                    time_str = f" ({' + '.join(parts)})" if parts else ""
                    text_parts[-1] = (text_parts[-1][0] + time_str + "]", color)


                seconds = insgesamt_time % 60
                minutes = insgesamt_time // 60

                if seconds == 1:
                    secondLabel = self.strings["Sekunde"]
                else:
                    secondLabel = self.strings["Sekunden"]
                
                if minutes == 1:
                    minuteLabel = self.strings["Minute"]
                else:
                    minuteLabel = self.strings["Minuten"]

                text_parts.append((path[i], "black"))
                route_window,
                title.config(text=(
                    f"{self.strings['Kürzeste Route von']} {start_station} {self.strings['nach']} {end_station}"
                    f"({minutes} {minuteLabel} {seconds} {secondLabel})"
                ),
                font=("Arial", 12, "bold")
                )
                for text, color in text_parts:
                    tk.Label(segment_frame, text=text,
                            font=("Arial", 12), fg=color,
                            bg=segment_frame["bg"]).pack(side="left", padx=5)






                

        def dijkstra(self, start_station):
            # helper: convert takt stored in various shapes into plain seconds (int)
            def _takt_to_int(t):
                if isinstance(t, int):
                    return t
                if isinstance(t, float):
                    return int(t)
                if isinstance(t, list) and t:
                    return _takt_to_int(t[0])
                if isinstance(t, str):
                    s = t.strip()
                    if s.isdigit():
                        return int(s)
                    # fallback: try float->int
                    try:
                        return int(float(s))
                    except Exception:
                        return 0
                return 0

            # helper: convert a travel_time raw value to int seconds
            def _parse_travel_time(v):
                if isinstance(v, (int, float)):
                    return int(v)
                if isinstance(v, list) and v:
                    return _parse_travel_time(v[0])
                if isinstance(v, str):
                    s = v.strip()
                    # support "M:S" or "MM:SS"
                    if ":" in s:
                        parts = s.split(":")
                        try:
                            if len(parts) == 2:
                                return int(parts[0]) * 60 + int(parts[1])
                            if len(parts) == 3:
                                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        except Exception:
                            return 0
                    try:
                        return int(float(s))
                    except Exception:
                        return 0
                return 0

            # helper: read current clock from self.uhrzeit to seconds since midnight
            def _current_clock_seconds():
                u = getattr(self, "uhrzeit", None)
                if not u:
                    return 0
                try:
                    # u is either [H, M, S] or [H, M, S, "AM"/"PM"]
                    hour = int(u[0])
                    minute = int(u[1])
                    second = int(u[2])
                    if len(u) >= 4 and isinstance(u[3], str):
                        ampm = u[3].upper()
                        if ampm.startswith("P") and hour < 12:
                            hour += 12
                        if ampm.startswith("A") and hour == 12:
                            hour = 0
                    # clamp into valid ranges
                    hour %= 24
                    minute %= 60
                    second %= 60
                    return hour * 3600 + minute * 60 + second
                except Exception:
                    return 0

            # -- init --
            distances = {station: float('inf') for station in self.stations}
            start_time_seconds = _current_clock_seconds()
            distances[start_station] = start_time_seconds   # <<--- use real clock time here
            previous_stations = {station: None for station in self.stations}
            previous_lines = {station: None for station in self.stations}
            segment_times = {station: 0 for station in self.stations}
            wait_times = {station: 0 for station in self.stations}
            visited = set()

            # Dijkstra main loop
            while len(visited) < len(self.stations):
                # find next unvisited with smallest distance
                min_station = None
                min_distance = float('inf')
                for st in self.stations:
                    if st not in visited and distances[st] < min_distance:
                        min_distance = distances[st]
                        min_station = st

                if min_station is None:
                    break

                visited.add(min_station)
                current_time = distances[min_station]   # time (seconds) when we are AT min_station

                for line_data in self.lines:
                    # line_data expected: ((line_name, canvas_id, takt), points, times, color)
                    if len(line_data) < 4:
                        continue

                    (line_name, canvas_id, takt_raw), points, times, color = line_data
                    takt_sec = _takt_to_int(takt_raw)

                    for i, (x, y, name) in enumerate(points):
                        if name != min_station:
                            continue

                        neighbors = []
                        if i > 0:
                            neighbors.append((points[i - 1][2], times[i - 1]))
                        if i < len(points) - 1:
                            neighbors.append((points[i + 1][2], times[i]))

                        for neighbor, travel_time_raw in neighbors:
                            travel_time = _parse_travel_time(travel_time_raw)

                            if neighbor in visited:
                                continue

                            # WAIT: compute wait at the station where you board (min_station),
                            # using the current_time (arrival time at min_station).
                            prev_line = previous_lines[min_station]
                            wait_time = 0
                            if prev_line is None or prev_line[0] != line_name:
                                # use your existing helper (it expects an int takt)
                                if takt_sec > 0:
                                    wait_time = self.calculate_wait_time(int(current_time), int(takt_sec))
                                else:
                                    wait_time = 0
                            else:
                                wait_time = 0  # staying on same line -> no platform wait

                            # total time to reach neighbor = time at station + wait + riding time
                            new_distance = current_time + wait_time + travel_time

                            if new_distance < distances[neighbor]:
                                distances[neighbor] = new_distance
                                previous_stations[neighbor] = min_station
                                previous_lines[neighbor] = (line_name, color)
                                segment_times[neighbor] = travel_time + wait_time
                                wait_times[neighbor] = wait_time

            return distances, previous_stations, previous_lines, segment_times, wait_times








        def remove_unused_points(self):
            used_points = set()
            for _, points, _, _ in self.lines:
                for _, _, name in points:
                    used_points.add(name)
            for name in list(self.stations.keys()):
                if name not in used_points:
                    del self.stations[name]
                    self.canvas.delete(name)
            for x, y, name in self.current_line:
                if name not in used_points:
                    self.current_line.remove((x, y, name))
        def komplexlinecreation(self, event=None):
            print(self.strings["Komplexe Stationserstellung"])

            komplex = tk.Toplevel(self.master)
            komplex.title(self.strings["Komplexe Stationserstellung"])
            komplex.bind("<Shift-Escape>", self.close_all_except_root)
            nameL = tk.Label(komplex, text=self.strings["Hier soll der Name der Station eingegeben werden:"])
            nameL.pack()

            self.nameE = tk.Entry(komplex, width=20)
            self.nameE.pack()

            proceed = tk.Button(komplex, text=self.strings["Weiter ->"], command=self.komplex)
            proceed.pack()

        def komplex(self):
            self.x = simpledialog.askinteger(self.strings["X-Koordinate"], self.strings["Was soll die x Koordinate, also die Koordinate von links nach rechts sein?"])
            self.y = simpledialog.askinteger(self.strings["Y-Koordinate"], self.strings["Was soll die y Koordinate, also die Koordinate von oben nach unten sein?"])
            if self.x and self.y:
                self.add_station(komplex=True)
        def add_station(self, event=None, komplex=False):
            
            if self.build_mode:
                if komplex == False:
                    x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
                    name = self.entry.get()
                    self.entry.delete(0, "end")
                elif komplex == True:
                    x = self.x
                    y = self.y
                    name = self.nameE.get()
                else:
                    return
                if name == "/komplex" or name == "/complex":
                    self.komplexlinecreation()
                    return

                if name not in self.stations:
                    if name == "":
                        proceed = messagebox.askyesno(self.strings["Bestätigen"], self.strings["Willst du wirklich eine Station ohne Namen erstellen?"])
                        if proceed == False:
                            return
                    self.stations[name] = [x, y]
                    self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black", tags=name)
                    print("Station wird erstellt: /name".replace("/name", name))
                    
                    self.canvas.create_text(x-15, y, text=name, anchor=tk.E, tags=name)
                    self.canvas.tag_bind(name, "<Button-3>", lambda e, station=name: self.stationWindow(station))


                self.current_line.append((x, y, name))

        def add_intermediate_stop(self, station):
            if self.build_mode:
                if station in self.stations:
                    x = self.stations[station][0]
                    y = self.stations[station][1]
                    self.current_line.append((x, y, station))
                else:
                    messagebox.showerror(self.strings["Fehler"], self.strings["Die Startstation 'start_station' existiert nicht.".replace("start_station", station)])
        def redraw(self):
            self.canvas.delete("all")
            for name, (x, y) in self.stations.items():
                self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")
                self.canvas.create_text(x - 15, y, text=name, anchor=tk.E, tags=name)
            for _, points, color in self.lines:
                coords = [(x, y) for x, y, _ in points]
                self.canvas.create_line(coords, fill=color)

        def showListOfConnectionsToDelete(self, event=None):
            lineList = tk.Toplevel(self.master)
            count = 0
            for line in self.lines:
                count += 1
                tk.Button(lineList, text=f"{line[0][0]}", bg=f"{line[-1]}", command=lambda line=line, station=None: self.lineinfo(line=line, station=None)).pack()
                lineList.title(self.strings["Alle Linien (insgesamt /count)"].replace("/count", str(count)))
        def delete_selected_connection(self):
            selected = self.listbox.curselection()
            if not selected:
                messagebox.showwarning(self.strings["Keine Auswahl"], self.strings["Bitte eine Verbindung auswählen."])
                return
            index = selected[0]

            # Entferne die Linie aus self.lines
            del self.lines[index]

            # Alles neu zeichnen
            self.redraw()

            # Entferne den Eintrag aus der Listbox
            self.listbox.delete(index)

            


        def add_intermediate_stop_prompt(self, event=None):
            if self.build_mode:
                station = simpledialog.askstring(self.strings["Umsteigemöglichkeit hinzufügen"], self.strings["Bitte geben Sie den Namen der Station ein:"])
                if station:
                    self.add_intermediate_stop(station)


        def minutes_and_seconds_to_seconds(self, time):
            minutes = time[0]
            seconds = time[1]
            seconds += 60 * minutes
            return seconds
        def create_line(self, event=None):
            if len(self.current_line) == 0:
                return

            start = self.current_line[0]
            end = self.current_line[-1]

            if len(self.current_line) > 1:
                name = simpledialog.askstring(self.strings["Name"], self.strings["Wie soll der Name der Linie lauten?"])
                if not name:
                    return

                for i, Line in enumerate(self.lines):
                    Name = Line[0][0]
                    existing_points = Line[1]
                    old_times = Line[2]
                    color = Line[3]

                    # Prüfen, ob Name gleich ist und Start/End anschließt
                    if name == Name and (
                        start == existing_points[0] or
                        start == existing_points[-1] or
                        end == existing_points[0] or
                        end == existing_points[-1]
                    ):
                        Append = messagebox.askyesno(self.strings["Anhängen"], "Es gibt schon eine Linie namens /name, willst du die neue anhängen?".replace("/name", name))
                        if Append:
                            # Richtige Richtung ermitteln
                            if start == existing_points[-1]:
                                new_points = self.current_line
                            elif end == existing_points[-1]:
                                new_points = self.current_line[::-1]
                            elif start == existing_points[0]:
                                new_points = self.current_line[::-1]
                                existing_points = existing_points[::-1]
                                old_times = old_times[::-1]
                            elif end == existing_points[0]:
                                new_points = self.current_line
                                existing_points = existing_points[::-1]
                                old_times = old_times[::-1]
                            else:
                                continue

                            # Zeiten abfragen
                            times = []
                            for j in range(len(new_points) - 1):
                                text = self.strings[
                                "Zeit zwischen /new_points[j][2] und /new_points[j+1][2] (in Sekunden):"
                                ]
                                

                                # Platzhalter ersetzen (beide müssen Strings sein)
                                text = text.replace("/new_points[j][2]", str(new_points[j][2]))
                                text = text.replace("/new_points[j+1][2]", str(new_points[j+1][2]))

                                # Dialog anzeigen
                                t = simpledialog.askstring(self.strings["Zeit"], text)
                                t = t.split(":")
                                if len(t) > 0:
                                    t = self.minutes_and_seconds_to_seconds(time=(int(t[0]), int(t[1])))

                                if t is None:
                                    return
                                times.append(t)

                            # Neue Punktliste und Zeitliste zusammenfügen
                            full_points = existing_points + new_points[1:]
                            full_times = old_times + times

                            # Alte Linie löschen und neue zeichnen
                            self.canvas.delete(Line[0][1])
                            canvas_line = self.canvas.create_line(
                                [self.stations[pt[2]][:2] for pt in full_points],
                                fill=color,
                                width=self.width
                            )

                            self.lines[i] = [[name, canvas_line], full_points, full_times, color]
                            self.current_line = []
                            return

                # Wenn keine passende Linie gefunden oder Anfügen abgelehnt wurde
                times = []
                takt = simpledialog.askstring(self.strings["Takt"], self.strings["Was soll der Takt der neuen Linie sein?"])
                takt = takt.split(":")
                if len(takt) > 1:
                    takt = self.minutes_and_seconds_to_seconds(time=(int(takt[0]), int(takt[1])))
                elif len(takt) == 0:
                    takt = int(takt[0])
                for i in range(len(self.current_line) - 1):
                    text = self.strings[
                        "Zeit zwischen /new_points[j][2] und /new_points[j+1][2] (in Sekunden):"
                    ]

                    #Hier i statt j verwenden
                    text = text.replace("/new_points[j][2]", str(self.current_line[i][2]))
                    text = text.replace("/new_points[j+1][2]", str(self.current_line[i + 1][2]))


                    t = simpledialog.askstring(self.strings["Zeit"], text)
                    t = t.split(":")
                    if len(t) > 1:
                        t = self.minutes_and_seconds_to_seconds(time=(int(t[0]), int(t[1])))
                    elif len(t) == 0:
                        t = int(t[0])
                    if t is None:
                        return
                    times.append(t)
                
                        



                self.line_color = self.line_color
                canvas_line = self.canvas.create_line(
                    [self.stations[pt[2]][:2] for pt in self.current_line],
                    fill=self.line_color,
                    width=self.width,
                )
                self.lines.append([[name, canvas_line, takt], self.current_line.copy(), times, self.line_color])
                self.current_line = []
            second = 0
            minute = 0
            hour = 0
            count = 0
            print(f"Zeiten{times} Takt{takt}")
            print(f"{self.lines[-1][1]}")
            #for station in self.lines[-1][1]:
                #if count >= len(times):
                    #print("Reached end of times list.")
                    #break
                #print(station[2])

                #print(f"{int(takt[0])}, {times[count][0]}")
                #if int(takt[0]) < int(times[count][0]):
                    #try:
                        #minute += int(takt[0])
                    #except IndexError:
                        #pass
                
                    #if minute >= 60:
                        #hour += minute // 60
                        #minute %= 60
                #else:
                    #print(times[count][0])
                    #minute += int(times[count][0])
                #print(f"Station: {station[2]} Stunde:{hour} Minute:{minute} Linie:{self.lines[-1][0][0]}")
                #self.stations[f"{station[2]}"] = {f"'{hour}:{minute}']": self.lines[-1][0][0]}

                #print(self.stations)

                #count += 1
                #if count == len(times) -1:
                    #break
            print(self.stations)
            print("===================")
            print(self.takt)
            station_start_time = [0, 0, 0]  # [hour, minute, second]

            for station in self.lines[-1][1]:  # Assuming this is a list of station info
                station_time = station_start_time.copy()
                
                while station_time[0] < 24:
                    stationname = station[2]  # Assuming station[2] is the station name

                    # Initialize the station entry if not already present
                    if stationname not in self.takt:
                        self.takt[stationname] = []

                    # Append the current time entry
                    self.takt[stationname].append({
                        name: {
                            f"{station_time[0]:02d}": {
                                f"{station_time[1]:02d}": {
                                    f"{station_time[2]:02d}": True
                                }
                            }
                        }
                    })

                    # Increment time
                    station_time[2] += int(takt[0])  # takt[0] is assumed to be in seconds

                    # Roll over seconds to minutes
                    if station_time[2] >= 60:
                        station_time[1] += station_time[2] // 60
                        station_time[2] %= 60

                    # Roll over minutes to hours
                    if station_time[1] >= 60:
                        station_time[0] += station_time[1] // 60
                        station_time[1] %= 60

            print(self.stations)
            print("===================")
            print(self.takt)

        def choose_color(self, event=None):
            color = colorchooser.askcolor(title=self.strings["Linienfarbe wählen"])
            if color[1]:
                self.line_color = color[1]

        def save_plan(self, event=None):
            self.remove_unused_points()
            filename = filedialog.asksaveasfilename(title=self.strings["Speichern unter"], defaultextension=".json", filetypes=[("JSON", "*.json")])
            if filename:
                if not filename.endswith(".json"):
                    filename += ".json"
                data = {
                    "lines": self.lines,
                    "stations": self.stations,
                    "build": self.bau
                }
                with open(filename, mode="w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo(self.strings["Gespeichert"], self.strings["Netzplan wurde als '/filename' gespeichert."].replace("/filename", filename))
                
        def load_plan(self, event=None):
            
            filename = filedialog.askopenfilename(title=self.strings["Laden"], defaultextension=".json", filetypes=[("JSON", "*.json")])
            if filename:
                if not filename.endswith(".json"):
                    filename += ".json"
                try:
                    with open(filename,mode="r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.lines = data["lines"]
                        self.stations = data["stations"]
                        self.bau = data["build"]
                except FileNotFoundError:
                    messagebox.showerror(self.strings["Fehler"], self.strings["Datei '/filename' wurde nicht gefunden."].replace("/filename", filename))
                    return

                # Notfalls leeren, aber weitermachen
                

                self.draw_lines()  # Jetzt korrekt nach dem Laden
                messagebox.showinfo(self.strings["Geladen"], self.strings["Netzplan '/filename' wurde geladen. Stationen: /self.stations"].replace("/filename", filename).replace("/self.stations", f"{self.stations}"))

                    
                print(self.stations)
                print(self.lines)
        def draw_lines(self):
            self.canvas.delete("all")
            for line, points, time, color in self.lines:
                self.canvas.create_line([self.stations[point[2]][:2] for point in points], fill=color, width=self.width)
                for x, y, name in points:
                    self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black",)
                    self.canvas.create_text(x-15, y, text=name, anchor=tk.E, tags=name)
                    self.canvas.tag_bind(name, "<Button-1>", lambda event, name=name: self.open_line_creation_window(name))

        def open_line_creation_window(self, name):
            if not self.build_mode:
                window = tk.Toplevel(self.master)
                window.bind("<Shift-Escape>", self.close_all_except_root)
                window.title(self.strings["Linie erstellen"])
                button = tk.Button(window, text=self.strings["Linie von /name erstellen"].replace("/name", name), command=lambda: self.start_line_creation(name))
                button.pack()

        def start_line_creation(self, name):
            self.current_line = [(x, y, n) for x, y, n in self.current_line if n == name]

        def toggle_build_mode(self, event=None):
            self.build_mode = not self.build_mode
            self.build_mode_button.config(text=self.strings["Bau-Modus deaktivieren"] if self.build_mode else self.strings["Bau-Modus aktivieren"])

        def move_canvas(self, dx, dy):
            self.canvas.xview_scroll(dx, "units")
            self.canvas.yview_scroll(dy, "units")
        def showListOfAllStations(self, event=None):
            self.list = tk.Toplevel(self.master)
            self.list.title(self.strings["Liste aller Stationen"])
            self.list.bind("<Shift-Escape>", self.close_all_except_root)
            self.searchEntry = tk.Entry(self.list, width=20)
            self.searchEntry.grid(row=0, column=0)
            searchButton = tk.Button(self.list, text=self.strings["Suchen"], command=self.searchF)
            searchButton.grid(row=0, column=1)
            varRow = 1
            varColumn = 0
            
            #myScrollbar = tk.Scrollbar(list, orient="vertical")
            #myScrollbar.grid(row=1, column=4)
            
            stops = sorted(self.stations)
            count = 0
            for stop in stops:
                if stop.startswith(self.search) == True:
                    nameOfStation = tk.Button(self.list, text=stop, command=lambda station=stop: self.stationWindow(station=station))

                    nameOfStation.grid(row= varRow, column=varColumn, sticky="nw")
                    if varRow < 24:
                        varRow += 1
                    else:
                        varColumn += 1
                        varRow = 1
                    count += 1
            self.list.title(self.strings["Liste aller Stationen (insgesamt /count)"].replace("/count", str(count)))
            
            #34 
        def rename(self,station):
            renameW = tk.Toplevel(self.master)
            renameW.title(self.strings["/station umbenennen"].replace("/station", station))
            renameW.bind("<Shift-Escape>", self.close_all_except_root)
            ueberschrift = tk.Label(renameW, text=self.strings["Wie soll /station in Zukunft heissen"].replace("/station", station))
            ueberschrift.pack()
            
            newNameEntry = tk.Entry(renameW, width=50)
            newNameEntry.pack()
            newNameEntry.insert(0, f"{station}")
            
            confirm = tk.Button(renameW, text=self.strings["Bestätigen"], command=lambda: self.Dorename(station=station, new=newNameEntry.get()))


            confirm.pack()
        def Dorename(self, station, new):
        # 1. Prüfen, ob der neue Name schon existiert
            if new in self.stations:
                messagebox.showerror(self.strings["Fehler"], self.strings["Name '/new' existiert bereits!"].replace("/new", new))
                return

            # 2. Stations-Dict atomar umbenennen
            coords = self.stations.pop(station)
            self.stations[new] = coords

            # 3. In allen Linien die Punkte umbenennen
            updated_lines = []
            for line_id, points, time, color in self.lines:
                new_points = []
                for x, y, name in points:
                    if name == station:
                        new_points.append((x, y, new))
                    else:
                        new_points.append((x, y, name))
                updated_lines.append((line_id, new_points, time, color))
            self.lines = updated_lines

        # 4. Aktuelle Linie (falls gerade im Erstellungsmodus) anpassen
            self.current_line = [
                (x, y, new) if name == station else (x, y, name)
                for (x, y, name) in self.current_line
        ]

        # 5. Canvas komplett neu zeichnen mit aktualisierten Daten
            self.draw_lines()
            self.close_all_except_root()

        # Erfolgsmeldung
            messagebox.showinfo(self.strings["Umbenannt"], self.strings["Station '/station' wurde zu '/new' umbenannt."].replace("/station", station).replace("/new", new))

        def confirmDeletion(self, line, window):
            confirm = messagebox.askyesno(self.strings["Löschen bestätigen"], self.strings["Möchtest du die Linie '/line[0][0]' wirklich löschen?"].replace("/line[0][0]", line[0][0]))
            if confirm:
                if line in self.lines:
                    self.lines.remove(line)
                    self.draw_lines()
                    window.destroy()
                    messagebox.showinfo(self.strings["Gelöscht"], self.strings["Die Linie '/line[0][0]' wurde gelöscht."].replace("/line[0][0]", line[0][0]))

        
        def delete_station(self, station):
            # 1. Aus stations-Dict entfernen
            if station in self.stations:
                del self.stations[station]
            # 2. Aus allen Linien entfernen
            new_lines = []
            for line_id, points, color in self.lines:
                filtered = [pt for pt in points if pt[2] != station]
                # Nur Linien behalten, die noch mindestens 2 Punkte haben
                if len(filtered) > 1:
                    new_lines.append((line_id, filtered, color))
            self.lines = new_lines
            # 3. Canvas komplett neu zeichnen
            self.draw_lines()
        def stopRouteFinding(self, stop_station):
            self.RouteFinder = False
            self.open_route_planner_window(start=self.start_station, stop=stop_station)
            
        def startRouteFinding(self, start_station):
            self.RouteFinder = True
            self.start_station = start_station 
            
        def changeName(self, line):
            self.lines.remove(line)
            new = simpledialog.askstring(self.strings["Neuer Name"], self.strings["Was soll der neue Name der Linie /line[0][0] sein?"].replace("/line[0][0]", line[0][0]))
            if new:
                line[0][0] = new
                self.lines.append(line)

        def changeColor(self, line):
            self.lines.remove(line)
            new = colorchooser.askcolor(line[-1])[1]
            if new:
                line[-1] = new
                self.lines.append(line)
                self.draw_lines()
        def changeTime(self, Line, number):
            self.lines.remove(Line)
            new = simpledialog.askinteger(self.strings["Zeit"], self.strings["Was soll die neue Reisezeit sein? (Die alte war /Line[-2][number])"].replace("/Line[-2][number]", f"{Line[-2][number]}"))
            if new:
                newList = Line[-2]
                newList[number] = new
                stations =Line[1]
                other_stuff = Line[0]
                color = Line[-1]

                newline = [other_stuff, stations, newList, color]
                
                self.lines.append(newline)
        def lineinfo(self, line, station):
            
            self.highlight_single_line(line)

            self.info = tk.Toplevel(self.master)
            count = 0
            


            name = tk.Label(self.info, text=f'{self.strings["Name:"]} {line[0][0]}')
            color = tk.Label(self.info, text=f'{self.strings["Farbe:"]} {line[-1]}', bg=f"{line[-1]}")
            taktOfLine = tk.Label(self.info, text=f'{self.strings["Takt:"]} {line[0][2][0]}')
            
            name.pack()
            color.pack()
            taktOfLine.pack()

            delete_button = tk.Button(
                self.info,
                text=self.strings["Diese Linie löschen"],
                fg="black",
                command=lambda: self.confirmDeletion(line, self.info)
            )
            delete_button.pack(pady=10)

            overStations = tk.LabelFrame(self.info, text=self.strings["Stationen:"], relief="solid")
            overStations.pack()
            self.info.bind("<Shift-Escape>", self.close_all_except_root)
            recolor_button = tk.Button(self.info, text=self.strings["Farbe ändern"], command=lambda line=line:self.changeColor(line=line))
            recolor_button.pack()
            rename_button = tk.Button(self.info, text=self.strings["Namen ändern"], command=lambda line=line: self.changeName(line=line))
            rename_button.pack()


            counter = 0

            for Astation in line[1]:
                stop = Astation[2]
                interchanges = []  

                for Aline in self.lines:
                    if Astation in Aline[1]:
                        if Aline[0][0] == line[0][0]:
                            continue
                        else:
                            interchanges.append(Aline[0][0])  # oder nur Aline[0], je nach Datenstruktur
                if count > 0:
                    thing = f"{line[-2][count-1]} -> {stop}"
                else:
                    thing = f"{stop}"
                for part in interchanges:
                    thing += f", {part}"
                    print(thing)

                if str(stop).strip() == str(station).strip() and station is not None:
                    show = tk.Button(overStations, text=f"{thing}", bg="red", command=lambda Line=line, number=count-1: self.changeTime(Line, number))
                    counter += 1
                


                else:
                    counter += 1
                    show = tk.Button(overStations, text=f"{thing}", command=lambda Line=line, number=count-1: self.changeTime(Line, number))

                show.pack()
                counter += 1


            self.info.title(self.strings["Information zur /line[0][0] (/count Station(en))"].replace("/line[0][0]", line[0][0]).replace("/count", f"{count}"))
            self.info.protocol("WM_DELETE_WINDOW", self.on_close)

            # Rückkehr zur normalen Darstellung, wenn Fenster geschlossen wird
        def on_close(self):
            self.restore_all_lines()
            self.info.destroy()

            


        def stationWindow(self, station, event=None):
                    #self.bau ist ein dictionary welches die Bauprojekte zeigt
                    
                    stationW = tk.Toplevel(self.master)
                    stationW.bind("<Shift-Escape>", self.close_all_except_root)
                    # self.lines: [(Name, identification_number[(koor, dina, ten, "name1"), (koor, dina, ten, "name2")], "color")]
                    name = tk.Label(stationW, text=f'{self.strings["Name:"]} {station}')
                    name.pack()
                    
                    coords = tk.Label(stationW, text=f'{self.strings["Koordinaten:"]} {self.stations[station][0]}, {self.stations[station][1]}')
                    coords.pack()
                    Ueber = tk.Label(stationW, text=self.strings["vorbeikommende Linien:"])
                    Ueber.pack()

                    for line in self.lines:
                        linename = line[0][0]   # e.g., "S1"
                        stations_fwd = line[1]  # Original direction
                        color = line[-1]        # e.g., "red"

                        directions = {
                            "forward": stations_fwd,
                            "reverse": stations_fwd[::-1]
                        }

                        for dir_name, stations in directions.items():

                            for i, linestation in enumerate(stations):
                                if linestation[2] == station:  # This is the current station
                                    # Determine the next station in this direction
                                    if i + 1 < len(stations):
                                        next_station = stations[i + 1][2]  # Name of next station
                                    else:
                                        next_station = self.strings["Endstation"]

                                    next_one = None
                                    departure = []

                                    for entry in self.takt[station][2:]:  # Skip metadata
                                        if linename in entry:
                                            time_data = entry[linename]  # e.g., {"14": {"53": {"10": True}}}

                                            for hour_str in sorted(time_data.keys(), key=int):
                                                hour = int(hour_str)
                                                if hour < int(self.uhrzeit[0]):
                                                    continue

                                                minutes_dict = time_data[hour_str]
                                                for minute_str in sorted(minutes_dict.keys(), key=int):
                                                    minute = int(minute_str)

                                                    if hour == int(self.uhrzeit[0]) and minute < int(self.uhrzeit[1]):
                                                        continue

                                                    second_dict = minutes_dict[minute_str]
                                                    for second_str in sorted(second_dict.keys(), key=int):
                                                        second = int(second_str)

                                                        current_h = int(self.uhrzeit[0])
                                                        current_m = int(self.uhrzeit[1])
                                                        current_s = int(self.uhrzeit[2])

                                                        if (
                                                            hour > current_h or
                                                            (hour == current_h and minute > current_m) or
                                                            (hour == current_h and minute == current_m and second > current_s)
                                                        ):
                                                            departure_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                                                            
                                                            departure.append(departure_time)
                                                            next_one = departure_time
                                                            break
                                                    if next_one:
                                                        break
                                                if next_one:
                                                    break

                                    if next_one:
                                        inter = tk.Button(
                                            stationW,
                                            text=f"{linename}, {self.strings['nächste Abfahrt:']} {departure[0]} {next_station}",
                                            bg=color,
                                            command=lambda line=line, station=station: self.lineinfo(line=line, station=station)
                                        )
                                        inter.pack()
                                        departure = []


                    renameButton = tk.Button(stationW, text=self.strings["/station umbenennen"].replace("/station", station), command=lambda station=station: self.rename(station=station))
                    renameButton.pack()
                    deleteButton = tk.Button(stationW, text=self.strings["/station löschen"].replace("/station", station), command=lambda station=station: self.delete_station(station=station))
                    deleteButton.pack()
                    stationW.title(self.strings["/station - Menü"].replace("/station", station))
                    if self.RouteFinder == False:
                        startFinding = tk.Button(stationW, text=self.strings["Routenplanung von /station starten"].replace("/station", station), command=lambda start_station=station: self.startRouteFinding(start_station=station))
                        startFinding.pack()
                    else:
                        ToHere = tk.Button(stationW, text=self.strings["Routenplanung bei /station beenden"].replace("/station", station), command=lambda stop_station=station: self.stopRouteFinding(stop_station=station))
                        ToHere.pack()
                    intermediate = tk.Button(stationW, text=self.strings["Diese Station als Umsteigestation hinzufügen"], command=lambda station=station: self.intermediateStopAtWindow(station=station))
                    intermediate.pack()
                    if station in self.bau:
                        for project in self.bau[station]:
                            try:
                                showTheWork = tk.Label(stationW, text=project)
                                showTheWork.pack()
                            except KeyError:
                                self.bau.uprade({station: []})
                    
                    addBuildLabel = tk.Label(stationW, text=self.strings["Bauprojekt hinzufügen"], bg="yellow")
                    addBuildLabel.pack()
                    self.addBuild = tk.Entry(stationW, width=30)
                    self.addBuild.pack()
                    addBuildButton = tk.Button(stationW, text=self.strings["Bauarbeit hinzufügen"], command=lambda station=station: self.addWIP(station=station))
                    addBuildButton.pack()
                    ripBuildButton = tk.Button(stationW, text=self.strings["Bauprojekt beenden"], command=lambda station=station: self.ripWIP(station=station))
                    ripBuildButton.pack()


        def intermediateStopAtWindow(self, station):
            if station:
                    self.add_intermediate_stop(station)
        def addWIP(self, station):
            newWIP = self.addBuild.get()
            if station in self.bau:
                self.bau[station].append(newWIP)
            else:
                self.bau.update({station: [newWIP]})
        def ripWIP(self, station):
                rip = simpledialog.askstring(self.strings["Bauarbeiten beenden"], self.strings["Welches Bauprojekt möchtest du beenden?"])
                if rip in self.bau[station]:
                    self.bau[station].remove(rip)
                else:
                    messagebox.showerror(self.strings["Fehler"], self.strings["Es gibt die Bauarbeit oder das Bauprojekt /rip nicht!"].replace("/rip", rip))

        def searchF(self):
            self.search = self.searchEntry.get()
            self.list.destroy()
            self.showListOfAllStations()
        def run(self):
            self.draw_lines()
            self.master.mainloop()
        def highlight_single_line(self, selected_line):
            self.canvas.delete("all")
            for line, points, time, color in self.lines:
                if line == selected_line[0]:
                    draw_color = color
                else:
                    draw_color = "#ededed"
                coords = [(x, y) for x, y, _ in points]
                self.canvas.create_line(coords, fill=draw_color, width=self.width)
                for x, y, name in points:
                    self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")
                    self.canvas.create_text(x - 15, y, text=name, anchor=tk.E, tags=name)

        def restore_all_lines(self):
            self.draw_lines()

        


    if __name__ == "__main__":
        root = tk.Tk()
        netzplaner = Netzplaner(root)
        
        netzplaner.run()

except Exception as e:
    import traceback
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.extract_tb(exc_tb)
    last_call = tb[-1]
    pyperclip.copy("https://github.com/sonstantin/Slimeline/issues")
    messagebox.showerror("Error", f"{e}\n\n\n Place: {last_call}\n\n\nPlease report the error here. We copied the link in your clipboard. If you press 'OK', we will copy the Error in your clipboard:\nhttps://github.com/sonstantin/Slimeline/issues")
    pyperclip.copy(str(e))
    
#Here was the place, I went stupid and copied Slimeline again!
