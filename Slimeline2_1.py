#pylint:disable=W0611
#pylint:disable=W0612
import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import pickle, json
from PIL import Image, ImageTk
import requests




class Netzplaner:
    def __init__(self, master):
        image_url = "https://static.wikia.nocookie.net/minecraft_de_gamepedia/images/c/cc/Schleim.png/revision/latest/scale-to-width-down/150?cb=20200403150614.png"
        response = requests.get(image_url)
        with open("schleim.png", "wb") as f:
            f.write(response.content)
        from PIL import Image
        print("Slimeline wird geladen")
        self.master = master
        self.master.title("Slimeline 2.1")
        self.image = Image.open("schleim.png")
        self.image = ImageTk.PhotoImage(self.image)
        self.master.iconphoto(True, self.image)
        self.master.bell()
        
        self.canvasBG = "white"
        self.RouteFinder = False
        
        self.canvas = tk.Canvas(self.master, bg=self.canvasBG, width=600, height=400)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.build_line = tk.Frame(self.master, relief="solid",borderwidth=5)
        self.build_line.pack(fill = tk.X)
        self.station_radius = 10

        self.bau = {}
        

        self.search = ""
        self.add_intermediate_stop_button = tk.Button(self.build_line, text="Umsteigemöglichkeit hinzufügen", command=self.add_intermediate_stop_prompt)
        self.add_intermediate_stop_button.pack()
        self.stations = {}
        self.lines = []
        self.current_line = []
        self.build_mode = True

        self.entry = tk.Entry(self.build_line)
        self.entry.pack(side=tk.TOP, fill=tk.X)

        self.canvas.bind("<Button-1>", self.add_station)

        self.create_line_button = tk.Button(self.build_line, text="Linie erstellen", command=self.create_line)
        self.create_line_button.pack()
        self.listbutton = tk.Button(self.master, text="Liste der Stationen und Verbindungen", command=self.lists)
        self.listbutton.pack()
        self.choose_color_button = tk.Button(self.master, text="Linienfarbe wählen", command=self.choose_color)
        self.choose_color_button.pack()

        # NEU: Separate Buttons für Speichern und Laden
        self.save_button = tk.Button(self.master, text="Speichern/Laden", command=self.saveOrLoad)
        self.save_button.pack()
        
        
        self.build_mode_button = tk.Button(self.master, text="Bau-Modus deaktivieren", command=self.toggle_build_mode)
        self.build_mode_button.pack()
        
        options = tk.Button(self.master, text="Optionen", command=self.options)
        options.pack(anchor="w")

        self.line_color = "green"
        
        self.arrow = tk.Frame(self.master, relief="solid", borderwidth=5)
        self.arrow.pack(side=tk.RIGHT)
        
        self.up_button = tk.Button(self.arrow, text="↑", command=lambda: self.move_canvas(0, -10))
        self.up_button.pack(side=tk.RIGHT)
        self.down_button = tk.Button(self.arrow, text="↓", command=lambda: self.move_canvas(0, 10))
        self.down_button.pack(side=tk.RIGHT)
        self.left_button = tk.Button(self.arrow, text="←", command=lambda: self.move_canvas(-10, 0))
        self.left_button.pack(side=tk.RIGHT)
        self.right_button = tk.Button(self.arrow, text="→", command=lambda: self.move_canvas(10, 0))
        self.right_button.pack(side=tk.RIGHT)
        
        self.WASD = False

        self.routebutton = tk.Button(self.master, text="Routenplaner öffnen", command=lambda start="", stop="": self.open_route_planner_window(start="", stop=""))
        self.routebutton.pack(side=tk.LEFT)

        self.master.bind("<Up>", lambda event: self.move_canvas(0, -10))
        self.master.bind("<Down>", lambda event: self.move_canvas(0, 10))
        self.master.bind("<Left>", lambda event: self.move_canvas(-10, 0))
        self.master.bind("<Right>", lambda event: self.move_canvas(10, 0))
        if self.WASD:

            self.master.bind("<W>", lambda event: self.move_canvas(0, -10))
            self.master.bind("<A>", lambda event: self.move_canvas(-10, 0))
            self.master.bind("<S>", lambda event: self.move_canvas(0, 10))
            self.master.bind("<D>", lambda event: self.move_canvas(10, 0))
        
        print("Das inizialisieren von Slimeline war erfolgreich!")
    def setOptions(self, canvasBG, uiBG):
        if canvasBG == "":
        
            canvasBG = colorchooser.askcolor(title="Hintergrundfarbe wählen")
            if uiBG[1]:
                self.uiBG = uiBG
                self.canvas.configure(bg=f"{canvasBG[1]}")
                self.canvas.configure(bg=f"{canvasBG[1]}")
            
        elif self.uiBG == "":
            uiBG = colorchooser.askcolor(title="Hintergrundfarbe wählen")
            if self.uiBG[1]:
            
                self.master.configure(bg=f"{self.uiBG[1]}")
                self.build_line.configure(bg=f"{self.uiBG[1]}")
            if uiBG == "black":
                        self.left_button.config(bg="black", fg="white")
        
        messagebox.showinfo("Information", f"""Der Hintergrund des
        Netzplans wurde auf
         '{canvasBG[1]}' gesetzt!""")
        self.master.update()
       
         
        
        #self.build_line.configure(bg=f"{uiBG}")
        
        
    def options(self):
        settings = tk.Toplevel(self.master)
        
        
        settings.title("Einstellungen")
        graphical = tk.LabelFrame(settings, text="Graphische Einstellungen", relief="solid", borderwidth=5)
        graphical.grid(row=0, column=0)
        canvasbgEntry = tk.Button(graphical, text="Bestimmen", command=lambda uiBG="bla", canvasBG="": self.setOptions(uiBG="bla", canvasBG=""))
        canvasbgEntry.grid(row=0, column=1)
        canvasbgLabel = tk.Label(graphical, text="Hintergrund des Plans bestimmen:")
        
        
        canvasbgLabel.grid(row=0, column=0)
        
        uiLabel = tk.Label(graphical, text="Hintergrund der Benutzeroberfläche bestimmen:")
        uiLabel.grid(row=1, column=0)
        uiEntry = tk.Button(graphical, text="Bestimmen", command=lambda uiBG="", canvasBG="bla": self.setOptions(uiBG="", canvasBG="bla"))
        uiEntry.grid(row=1, column=1)
        
        
       
    def saveOrLoad(self):
        Auswahl = tk.Toplevel(self.master)
        Auswahl.title("Auswahl zum Speichern oder Laden")
        SaveButton = tk.Button(Auswahl, text="Speichern", command=self.save_plan)
        SaveButton.pack()
        LoadButton = tk.Button(Auswahl, text="Laden", command=self.load_plan)
        LoadButton.pack()
        
    def open_route_planner_window(self, start, stop):
        window = tk.Toplevel(self.master)
        window.title("Routenplaner")

        start_label = tk.Label(window, text="Startstation:")
        start_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.start_entry = tk.Entry(window)
        self.start_entry.grid(row=0, column=1, padx=10, pady=5)

        end_label = tk.Label(window, text="Zielstation:")
        end_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.end_entry = tk.Entry(window)
        self.end_entry.grid(row=1, column=1, padx=10, pady=5)
        self.start_entry.insert(0, start)
        self.end_entry.insert(0, stop)

        calculate_button = tk.Button(window, text="Route berechnen", command=self.calculate_route)
        calculate_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
    def lists(self):
        ask = tk.Toplevel(self.master)
        ask.title("Listen")
        OfStations = tk.Button(ask, text="Liste aller Stationen zeigen", command=self.showListOfAllStations)
        OfStations.pack()
        OfLines = tk.Button(ask, text="Liste aller Verbindungen zeigen", command=self.showListOfConnectionsToDelete)
        OfLines.pack()
    def calculate_route(self):
        start_station = self.start_entry.get()
        end_station = self.end_entry.get()

        if start_station not in self.stations:
            messagebox.showerror("Fehler", f"Die Startstation '{start_station}' existiert nicht.")
            return
        if end_station not in self.stations:
            messagebox.showerror("Fehler", f"Die Zielstation '{end_station}' existiert nicht.")
            return

        distances, previous_stations, previous_lines = self.dijkstra(start_station)
        if distances[end_station] == float('inf'):
            messagebox.showinfo("Information", "Es gibt keine Verbindung zwischen den Stationen.")
            return

        path = []
        lines_used = []
        station = end_station
        while station:
            path.insert(0, station)
            lines_used.insert(0, previous_lines.get(station))
            station = previous_stations[station]

        route_window = tk.Toplevel(self.master)
        route_window.title(f"Route von {start_station} nach {end_station}")

        title = tk.Label(route_window, text=f"Kürzeste Route von {start_station} nach {end_station} ({distances[end_station] + 1} Stationen):", font=("Arial", 12, "bold"))
        title.pack(pady=10)

        container = tk.Frame(route_window)
        container.pack(padx=10, pady=5)

        for i in range(len(path)):
            segment_frame = tk.Frame(container, bg="#f0f0f0" if i % 2 == 0 else "#ffffff", pady=5)
            segment_frame.pack(fill="x", padx=5, pady=1)

            text_parts = []

            if i > 0 and lines_used[i]:
                line_name, color = lines_used[i]
                text_parts.append(("→", "black"))
                text_parts.append((f"[{line_name[0]}]", color))

            text_parts.append((path[i], "black"))

            for text, color in text_parts:
                label = tk.Label(segment_frame, text=text, font=("Arial", 12), fg=color, bg=segment_frame["bg"])
                label.pack(side="left", padx=5)


            

    def dijkstra(self, start_station):
        distances = {station: float('inf') for station in self.stations}
        distances[start_station] = 0
        previous_stations = {station: None for station in self.stations}
        previous_lines = {station: None for station in self.stations}
        visited = set()

        while len(visited) < len(self.stations):
            min_distance = float('inf')
            min_station = None
            for station in self.stations:
                if station not in visited and distances[station] < min_distance:
                    min_distance = distances[station]
                    min_station = station
            if min_station is None:
                break
            visited.add(min_station)
            for line_name, points, color in self.lines:
                for i, (x, y, name) in enumerate(points):
                    if name == min_station:
                        neighbors = []
                        if i > 0:
                            neighbors.append(points[i-1][2])
                        if i < len(points) - 1:
                            neighbors.append(points[i+1][2])
                        for neighbor in neighbors:
                            if neighbor not in visited:
                                new_distance = distances[min_station] + 1
                                if new_distance < distances[neighbor]:
                                    distances[neighbor] = new_distance
                                    previous_stations[neighbor] = min_station
                                    previous_lines[neighbor] = (line_name, color)
        return distances, previous_stations, previous_lines


    def remove_unused_points(self):
        used_points = set()
        for _, points, _ in self.lines:
            for _, _, name in points:
                used_points.add(name)
        for name in list(self.stations.keys()):
            if name not in used_points:
                del self.stations[name]
                self.canvas.delete(name)
        for x, y, name in self.current_line:
            if name not in used_points:
                self.current_line.remove((x, y, name))

    def add_station(self, event):
        if self.build_mode:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            name = self.entry.get()
            self.entry.delete(0, "end")
            
            if name not in self.stations:
                if name == "":
                    proceed = messagebox.askyesno("Bestätigen", """Willst du wirklich eine
   Station ohne Namen
   erstellen?""")
                    if proceed == False:
                        return
                self.stations[name] = (x, y)
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")
                print(f"Station wird erstellt: {name!r}")
                
                self.canvas.create_text(x-15, y, text=name, anchor=tk.E, tags=name)
            self.current_line.append((x, y, name))

    def add_intermediate_stop(self, station):
        if self.build_mode:
            if station in self.stations:
                x, y = self.stations[station]
                self.current_line.append((x, y, station))
            else:
                messagebox.showerror("Fehler", f"Die Station '{station}' existiert nicht.")
    def redraw(self):
        self.canvas.delete("all")
        for name, (x, y) in self.stations.items():
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")
            self.canvas.create_text(x - 15, y, text=name, anchor=tk.E, tags=name)
        for _, points, color in self.lines:
            coords = [(x, y) for x, y, _ in points]
            self.canvas.create_line(coords, fill=color)

    def showListOfConnectionsToDelete(self):
        if not self.lines:
            messagebox.showinfo("Keine Verbindungen", "Es sind keine Verbindungen vorhanden.")
            return

        self.connection_window = tk.Toplevel(self.master)
        self.connection_window.title("Linien")
    
        scrollbar = tk.Scrollbar(self.connection_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(self.connection_window, yscrollcommand=scrollbar.set, width=60, height=15)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Verbindungseinträge zur Anzeige vorbereiten
        for idx, (_, points, color) in enumerate(self.lines):
            stations = " → ".join(point[2] for point in points)
            self.listbox.insert(tk.END, f"Linie {idx + 1}: {stations} (Farbe: {color})")

        scrollbar.config(command=self.listbox.yview)
        delete_button = tk.Button(self.connection_window, text="Ausgewählte Linie löschen", command=self.delete_selected_connection)
        delete_button.pack(pady=5)
    def delete_selected_connection(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Keine Auswahl", "Bitte eine Verbindung auswählen.")
            return
        index = selected[0]

        # Entferne die Linie aus self.lines
        del self.lines[index]

        # Alles neu zeichnen
        self.redraw()

        # Entferne den Eintrag aus der Listbox
        self.listbox.delete(index)

        


    def add_intermediate_stop_prompt(self):
        if self.build_mode:
            station = simpledialog.askstring("Umsteigemöglichkeit hinzufügen", "Bitte geben Sie den Namen der Station ein:")
            if station:
                self.add_intermediate_stop(station)

    def create_line(self):
        if len(self.current_line) > 1:
            name = simpledialog.askstring("Name", "Wie soll der Name der Linie lauten?")
            for Line in self.lines:
                Name = Line[0][0]
                if name == Name:
                    Append = messagebox.askyesno("Anhängen", f"Es gibt schon eine Linie namens {name}, willst du die neue anhängen?")
                    #messagebox.showinfo("Ja", f"{Append}")
                    if Append == True:
                        
                        self.line_color = f"{Line[-1]}"
            line = (name, self.canvas.create_line([self.stations[point[2]][:2] for point in self.current_line], fill=self.line_color))
            self.lines.append((line, self.current_line, self.line_color))
            self.current_line = []

    def choose_color(self):
        color = colorchooser.askcolor(title="Linienfarbe wählen")
        if color[1]:
            self.line_color = color[1]

    def save_plan(self):
        self.remove_unused_points()
        filename = simpledialog.askstring("Speichern unter", """Dateiname für den Netzplan eingeben: 
        (Merken Sie
        sich den Namen der Datei!)""")
        if filename:
            if not filename.endswith(".json"):
                filename += ".json"
            with open(filename, mode="w", encoding="utf-8") as f:
                json.dump([self.lines, self.stations], f)
            with open("Bau " + filename, "wb") as build:
                pickle.dump(self.bau, build)
            messagebox.showinfo("Gespeichert", f"Netzplan wurde als '{filename}' gespeichert.")
            
    def load_plan(self):
        filename = simpledialog.askstring("Laden", """Name der Datei, die geladen werden soll:
            """)
            
        if filename:
            if not filename.endswith(".json"):
                filename += ".json"
            try:
                with open(filename,mode="r", encoding="utf-8") as f:
                    liste = json.load(f)
                    self.lines = liste[0]
                    self.stations = liste[1]
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Datei '{filename}' wurde nicht gefunden.")
                return

            try:
                with open("Bau " + filename, "rb") as build:
                    self.bau = pickle.load(build)
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Datei 'Bau {filename}' wurde nicht gefunden.")
                self.bau = {}  # Notfalls leeren, aber weitermachen
            

            self.draw_lines()  # Jetzt korrekt nach dem Laden
            messagebox.showinfo("Geladen", f"Netzplan '{filename}' wurde geladen.\n\nStationen:\n{self.stations}")

                
            print(self.stations)
            print(self.lines)
    def draw_lines(self):
        self.canvas.delete("all")
        for line, points, color in self.lines:
            self.canvas.create_line([self.stations[point[2]][:2] for point in points], fill=color)
            for x, y, name in points:
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black",)
                self.canvas.create_text(x-15, y, text=name, anchor=tk.E, tags=name)
                self.canvas.tag_bind(name, "<Button-1>", lambda event, name=name: self.open_line_creation_window(name))

    def open_line_creation_window(self, name):
        if not self.build_mode:
            window = tk.Toplevel(self.master)
            window.title("Linie erstellen")
            button = tk.Button(window, text=f"Linie von {name} erstellen", command=lambda: self.start_line_creation(name))
            button.pack()

    def start_line_creation(self, name):
        self.current_line = [(x, y, n) for x, y, n in self.current_line if n == name]

    def toggle_build_mode(self):
        self.build_mode = not self.build_mode
        self.build_mode_button.config(text="Bau-Modus deaktivieren" if self.build_mode else "Bau-Modus aktivieren")

    def move_canvas(self, dx, dy):
        self.canvas.xview_scroll(dx, "units")
        self.canvas.yview_scroll(dy, "units")
    def showListOfAllStations(self):
        self.list = tk.Toplevel(self.master)
        self.list.title("Liste aller Stationen")
        
        self.searchEntry = tk.Entry(self.list, width=20)
        self.searchEntry.grid(row=0, column=0)
        searchButton = tk.Button(self.list, text="Suchen", command=self.searchF)
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
        self.list.title(f"Liste aller Stationen (insgesamt {count})")
        
         #34 
    def rename(self,station):
        renameW = tk.Toplevel(self.master)
        renameW.title(f"{station} umbenennen")
        
        ueberschrift = tk.Label(renameW, text=f"Wie soll {station} in Zukunft heissen")
        ueberschrift.pack()
        
        newNameEntry = tk.Entry(renameW, width=50)
        newNameEntry.pack()
        newNameEntry.insert(0, f"{station}")
        
        confirm = tk.Button(renameW, text="Bestätigen", command=lambda: self.Dorename(station=station, new=newNameEntry.get()))


        confirm.pack()
    def Dorename(self, station, new):
    # 1. Prüfen, ob der neue Name schon existiert
        if new in self.stations:
            messagebox.showerror("Fehler", f"Name '{new}' existiert bereits!")
            return

        # 2. Stations-Dict atomar umbenennen
        coords = self.stations.pop(station)
        self.stations[new] = coords

        # 3. In allen Linien die Punkte umbenennen
        updated_lines = []
        for line_id, points, color in self.lines:
            new_points = []
            for x, y, name in points:
                if name == station:
                    new_points.append((x, y, new))
                else:
                    new_points.append((x, y, name))
            updated_lines.append((line_id, new_points, color))
        self.lines = updated_lines

    # 4. Aktuelle Linie (falls gerade im Erstellungsmodus) anpassen
        self.current_line = [
            (x, y, new) if name == station else (x, y, name)
            for (x, y, name) in self.current_line
    ]

    # 5. Canvas komplett neu zeichnen mit aktualisierten Daten
        self.draw_lines()

    # Erfolgsmeldung
        messagebox.showinfo("Umbenannt", f"Station '{station}' wurde zu '{new}' umbenannt.")

    def confirmDeletion(self, line, window):
        confirm = messagebox.askyesno("Löschen bestätigen", f"Möchtest du die Linie '{line[0][0]}' wirklich löschen?")
        if confirm:
            if line in self.lines:
                self.lines.remove(line)
                self.draw_lines()
                window.destroy()
                messagebox.showinfo("Gelöscht", f"Die Linie '{line[0][0]}' wurde gelöscht.")


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
        
    def lineinfo(self, line):
        self.highlight_single_line(line)

        self.info = tk.Toplevel(self.master)
        self.info.title(f"Information zur {line[0][0]}")

        name = tk.Label(self.info, text=f"Name: {line[0][0]}")
        color = tk.Label(self.info, text=f"Farbe: {line[-1]}", bg=f"{line[-1]}")
        name.pack()
        color.pack()

        delete_button = tk.Button(
            self.info,
            text="Diese Linie löschen",
            fg="white",
            command=lambda: self.confirmDeletion(line, self.info)
        )
        delete_button.pack(pady=10)
        

        # Rückkehr zur normalen Darstellung, wenn Fenster geschlossen wird
    def on_close(self):
        self.restore_all_lines()
        self.info.destroy()

        self.info.protocol("WM_DELETE_WINDOW", self.on_close)


    def stationWindow(self, station):
                #self.bau ist ein dictionary welches die Bauprojekte zeigt
                stationW = tk.Toplevel(self.master)
                # self.lines: [(Name, identification_number[(koor, dina, ten, "name1"), (koor, dina, ten, "name2")], "color")]
                name = tk.Label(stationW, text=f"Name: {station}")
                name.pack()
                
                coords = tk.Label(stationW, text=f"Koordinaten: {self.stations[station]}")
                coords.pack()
                Ueber= tk.Label(stationW, text="vorbeikommende Linien:")
                Ueber.pack()
                for line in self.lines:
                    linename = line[0][0]
                    stations = line[1]
                    for linestation in stations:
                        name = linestation[2]
                        color = line[-1]
                        if name == station:
                            inter = tk.Button(stationW, text=linename, bg=f"{color}", command=lambda line=line: self.lineinfo(line=line))
                            inter.pack()
                        
                renameButton = tk.Button(stationW, text=f"{station} umbenennen", command=lambda station=station: self.rename(station=station))
                renameButton.pack()
                deleteButton = tk.Button(stationW, text=f"{station} löschen", command=lambda station=station: self.confirmDeletion(station=station))
                deleteButton.pack()
                stationW.title(f"{station} - Menü")
                if self.RouteFinder == False:
                    startFinding = tk.Button(stationW, text=f"Routenplanung von {station} starten", command=lambda start_station=station: self.startRouteFinding(start_station=station))
                    startFinding.pack()
                else:
                    ToHere = tk.Button(stationW, text=f"Routenplanung bei {station} beenden", command=lambda stop_station=station: self.stopRouteFinding(stop_station=station))
                    ToHere.pack()
                intermediate = tk.Button(stationW, text="Diese Station als Umsteigestation hinzufügen", command=lambda station=station: self.intermediateStopAtWindow(station=station))
                intermediate.pack()
                if station in self.bau:
                    for project in self.bau[station]:
                        try:
                            showTheWork = tk.Label(stationW, text=project)
                            showTheWork.pack()
                        except KeyError:
                            self.bau.uprade({station: []})
                
                addBuildLabel = tk.Label(stationW, text="Bauprojekt hinzufügen", bg="yellow")
                addBuildLabel.pack()
                self.addBuild = tk.Entry(stationW, width=30)
                self.addBuild.pack()
                addBuildButton = tk.Button(stationW, text="Bauarbeit hinzufügen", command=lambda station=station: self.addWIP(station=station))
                addBuildButton.pack()
                ripBuildButton = tk.Button(stationW, text="Bauprojekt beenden", command=lambda station=station: self.ripWIP(station=station))
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
              rip = simpledialog.askstring("Bauarbeiten beenden", "Welches Bauprojekt möchtest du beenden?")
              if rip in self.bau[station]:
                  self.bau[station].remove(rip)
              else:
                  messagebox.showerror("Fehler", f"Es gibt die Bauarbeit oder das Bauprojekt {rip} nicht!")

    def searchF(self):
        self.search = self.searchEntry.get()
        self.list.destroy()
        self.showListOfAllStations()
    def run(self):
        self.draw_lines()
        self.master.mainloop()
    def highlight_single_line(self, selected_line):
        self.canvas.delete("all")
        for line, points, color in self.lines:
            if line == selected_line[0]:
                draw_color = color
            else:
                draw_color = "gray"
            coords = [(x, y) for x, y, _ in points]
            self.canvas.create_line(coords, fill=draw_color)
            for x, y, name in points:
                self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")
                self.canvas.create_text(x - 15, y, text=name, anchor=tk.E, tags=name)

    def restore_all_lines(self):
        self.draw_lines()


if __name__ == "__main__":
    root = tk.Tk()
    netzplaner = Netzplaner(root)
    netzplaner.run()

        
