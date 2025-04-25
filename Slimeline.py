import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import pickle


class Netzplaner:
    def __init__(self, master):
        
        print("Slimeline wird geladen")
        self.master = master
        self.master.title("Slimeline 1.1")
        self.master.bell()
        
        self.canvasBG = "white"
        self.RouteFinder = False
        
        self.canvas = tk.Canvas(self.master, bg=self.canvasBG, width=600, height=400)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.build_line = tk.Frame(self.master, relief="solid",borderwidth=5)
        self.build_line.pack(fill = tk.X)
        self.station_radius = 10

        self.bau = {}
        


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
        self.listbutton = tk.Button(self.master, text="Liste der Stationen", command=self.showListOfAllStations)
        self.listbutton.pack()
        self.choose_color_button = tk.Button(self.master, text="Linienfarbe wählen", command=self.choose_color)
        self.choose_color_button.pack()

        # NEU: Separate Buttons für Speichern und Laden
        self.save_button = tk.Button(self.master, text="Speichern/Laden", command=self.saveOrLoad)
        self.save_button.pack()
        

        self.build_mode_button = tk.Button(self.master, text="Bau-Modus deaktivieren", command=self.toggle_build_mode)
        self.build_mode_button.pack()
        
        options = tk.Button(self.master, text="Optionen", command=self.options)
        options.place(anchor="w", y=1965, x=30)

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
        


        self.routebutton = tk.Button(self.master, text="Routenplaner öffnen", command=lambda start="", stop="": self.open_route_planner_window(start="", stop=""))
        self.routebutton.pack(side=tk.LEFT)

        self.master.bind("<Up>", lambda event: self.move_canvas(0, -10))
        self.master.bind("<Down>", lambda event: self.move_canvas(0, 10))
        self.master.bind("<Left>", lambda event: self.move_canvas(-10, 0))
        self.master.bind("<Right>", lambda event: self.move_canvas(10, 0))
        #self.master.bind("<W>", lambda event: self.move_canvas(0, -10))
        #self.master.bind("<A>", lambda event: self.move_canvas(-10, 0))
        #self.master.bind("<S>", lambda event: self.move_canvas(0, 10))
        #self.master.bind("<D>", lambda event: self.move_canvas(10, 0))
        
        print("Das inizialisieren von Slimeline war erfolgreich!")
    def setOptions(self, canvasBG, uiBG):
        
        
        self.canvasBG = canvasBG
        messagebox.showinfo("Information", f"""Der Hintergrund des
        Netzplans wurde auf
         '{canvasBG}' gesetzt!""")
        self.master.update()
       
         
        self.master.configure(bg=f"{uiBG}")
        self.build_line.configure(bg=f"{uiBG}")
        
        if uiBG == "black":
            self.left_button.config(bg="black", fg="white")
    def options(self):
        settings = tk.Toplevel(self.master)
        
        
        settings.title("Einstellungen")
        graphical = tk.LabelFrame(settings, text="Graphische Einstellungen", relief="solid", borderwidth=5)
        graphical.grid(row=0, column=0)
        canvasbgEntry = tk.Entry(graphical, width=10)
        canvasbgEntry.grid(row=0, column=1)
        canvasbgLabel = tk.Label(graphical, text="Hintergrund des Plans:")
        
        
        canvasbgLabel.grid(row=0, column=0)
        canvasbgEntry.insert(0, self.canvasBG)
        uiLabel = tk.Label(graphical, text="Hintergrund der Benutzeroberfläche:")
        uiLabel.grid(row=1, column=0)
        uiEntry = tk.Entry(graphical,  width=10)
        uiEntry.grid(row=1, column=1)
        
        
        confirmgraphical = tk.Button(graphical, text="Graphisches Bestätigen", command=lambda: self.setOptions(canvasBG=canvasbgEntry.get(), uiBG=uiEntry.get()))
        confirmgraphical.grid(row=10, column=1)
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
        

    def calculate_route(self):
        start_station = self.start_entry.get()
        end_station = self.end_entry.get()

        if start_station not in self.stations:
            messagebox.showerror("Fehler", f"Die Startstation '{start_station}' existiert nicht.")
            return
        if end_station not in self.stations:
            messagebox.showerror("Fehler", f"Die Zielstation '{end_station}' existiert nicht.")
            return

        distances, previous_stations = self.dijkstra(start_station)
        if distances[end_station] == float('inf'):
            messagebox.showinfo("Information", "Es gibt keine Verbindung zwischen den Stationen.")
        else:
            path = []
            station = end_station
            while station:
                path.insert(0, station)
                station = previous_stations[station]
            route_info = f"""Die kürzeste Route von:
             {start_station} nach: 
            {end_station} beträgt
             {distances[end_station] + 1} Station(en).\nRoute:
            	 {'''->
            	  '''.join(path)}"""
            messagebox.showinfo("Information", route_info)

    def dijkstra(self, start_station):
        distances = {station: float('inf') for station in self.stations}
        distances[start_station] = 0
        previous_stations = {station: None for station in self.stations}
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
            for line, points, _ in self.lines:
                for i, (x, y, name) in enumerate(points):
                    if name == min_station:
                        if i > 0:
                            neighbor = points[i-1][2]
                            if neighbor not in visited:
                                new_distance = distances[min_station] + 1
                                if new_distance < distances[neighbor]:
                                    distances[neighbor] = new_distance
                                    previous_stations[neighbor] = min_station
                        if i < len(points) - 1:
                            neighbor = points[i+1][2]
                            if neighbor not in visited:
                                new_distance = distances[min_station] + 1
                                if new_distance < distances[neighbor]:
                                    distances[neighbor] = new_distance
                                    previous_stations[neighbor] = min_station
        return distances, previous_stations

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
                self.stations[name] = (x, y)
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")
                self.canvas.create_text(x-15, y, text=name, anchor=tk.E, tags=name)
            self.current_line.append((x, y, name))

    def add_intermediate_stop(self, station):
        if self.build_mode:
            if station in self.stations:
                x, y = self.stations[station]
                self.current_line.append((x, y, station))
            else:
                messagebox.showerror("Fehler", f"Die Station '{station}' existiert nicht.")

    def add_intermediate_stop_prompt(self):
        if self.build_mode:
            station = simpledialog.askstring("Umsteigemöglichkeit hinzufügen", "Bitte geben Sie den Namen der Station ein:")
            if station:
                self.add_intermediate_stop(station)

    def create_line(self):
        if len(self.current_line) > 1:
            line = self.canvas.create_line([self.stations[point[2]][:2] for point in self.current_line], fill=self.line_color)
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
            if not filename.endswith(".pkl"):
                filename += ".pkl"
            with open(filename, "wb") as f:
                pickle.dump((self.lines, self.stations), f)
            with open("Bau " + filename, "wb") as build:
                pickle.dump(self.bau, build)
            messagebox.showinfo("Gespeichert", f"Netzplan wurde als '{filename}' gespeichert.")

    def load_plan(self):
        filename = simpledialog.askstring("Laden", """Name der Datei, die geladen werden soll:
             """)
             
        if filename:
            if not filename.endswith(".pkl"):
                filename += ".pkl"
            try:
                with open(filename, "rb") as f:
                    self.lines, self.stations = pickle.load(f)
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Datei '{filename}' wurde nicht gefunden.")
            try:
                with open("Bau " + filename, "rb") as build:
                    self.bau = pickle.load(build)
            except FileNotFoundError:
                messagebox.showerror("Fehler", f"Datei 'Bau {filename}' wurde nicht gefunden.")
                self.draw_lines()
                string = f"Netzplan '{filename}' wurde geladen."
                string = f"""{string} {self.stations}"""  #Dann wird self.stations angezeigt!
                
                '''self.stations = {
                "Name der Station": koordinaten als int,
                [...]
                }'''
                messagebox.showinfo("Geladen", string)
            
                

    def draw_lines(self):
        self.canvas.delete("all")
        for line, points, color in self.lines:
            self.canvas.create_line([self.stations[point[2]][:2] for point in points], fill=color)
            for x, y, name in points:
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")
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
        list = tk.Toplevel(self.master)
        list.title("Liste aller Stationen")
        
        
        varRow = 1
        varColumn = 0
        
        #myScrollbar = tk.Scrollbar(list, orient="vertical")
        #myScrollbar.grid(row=1, column=4)
        
        stops = sorted(self.stations)
        count = 0
        for stop in stops:
            nameOfStation = tk.Button(list, text=stop, command=lambda station=stop: self.stationWindow(station=station))

            nameOfStation.grid(row= varRow, column=varColumn, sticky="nw")
            if varRow < 24:
                varRow += 1
            else:
                varColumn += 1
                varRow = 1
            count += 1
        list.title(f"Liste aller Stationen (insgesamt {count})")
        
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

    def confirmDeletion(self, station):
        answer = simpledialog.askstring("Bestätigung", f'Schreibe "ok" oder "OK" in das Textfeld, um "{station}" zu löschen!')
        if answer and answer.lower() == "ok":
            self._delete_station(station)
            messagebox.showinfo("Gelöscht", f'Station "{station}" wurde gelöscht.')
        else:
            messagebox.showinfo("Abgebrochen", "Löschvorgang abgebrochen.")

    def _delete_station(self, station):
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

    def stationWindow(self, station):
                #self.bau ist ein dictionary welches die Bauprojekte zeigt
                stationW = tk.Toplevel(self.master)
                
                name = tk.Label(stationW, text=f"Name: {station}")
                name.pack()
                
                coords = tk.Label(stationW, text=f"Koordinaten: {self.stations[station]}")
                coords.pack()
                
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
              
    def run(self):
        self.draw_lines()
        self.master.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    netzplaner = Netzplaner(root)
    netzplaner.run()

        
