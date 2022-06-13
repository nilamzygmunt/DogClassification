import psycopg2

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from model import Classificator
from dogimage import DogImage
from kivy.properties import ObjectProperty

class ScreenOne(Screen):
    pass

class ScreenTwo(Screen):
    image = ObjectProperty(None)

    def selected(self, filename):
        self.ids.image.source = filename[0]
        self.ids.image.color = (1,1,1.1)
        self.ids.image.reload()
        self.ids.upload_button.disabled = False
        
        print(self.image.source)

    def get_image_path(self):
        return self.image.source 


class ScreenThree(Screen):
    chosen = ObjectProperty(None)
    prediction_breed = ""
    def prediction(self):
        self.prediction_breed = app.get_model().predictBreed(self.chosen.source)
        pred_text = "The predicted breed is " 
        app.get_dog_image().set_breed(self.prediction_breed)
        app.get_dog_image().set_path(self.chosen.source)
        print (self.prediction_breed)
        return pred_text + self.prediction_breed


class ScreenFour(Screen):
    
    chosen = ObjectProperty(None)
    def save_to_db(self):
        if not app.get_database().track_exists(self.chosen.source):
            print("saving")
            app.get_database().execute("INSERT INTO Dogs VALUES (%s, %s)", (app.get_dog_image().get_path(), app.get_dog_image().get_breed()))
    



class Database:
    def __init__(self, name):
        self._conn = psycopg2.connect(name)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self,):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def track_exists(self, track_id):
        cur = self.cursor
        cur.execute("SELECT id FROM Dogs WHERE id = %s", (track_id,))
        return cur.fetchone() is not None  

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

class dog_dbApp(App):
    screen_manager = ScreenManager()
    _classifydog = Classificator() 
    _database = Database("dbname=app_database user=app_user password=app_password")
    _dog_image = DogImage()
    def build(self):
        self._classifydog.loadBreeds("labels.csv")
        self._classifydog.loadModel("model")
        screen_one = ScreenOne()
        screen_two = ScreenTwo()
        screen_three = ScreenThree()
        screen_four = ScreenFour()
        
        self.screen_manager.add_widget(screen_one)
        self.screen_manager.add_widget(screen_two)
        self.screen_manager.add_widget(screen_three)
        self.screen_manager.add_widget(screen_four)
        return self.screen_manager

    def get_model(self):
        return self._classifydog

    def get_database(self):
        return self._database

    def get_dog_image(self):
        return self._dog_image


if __name__ == "__main__":
    app = dog_dbApp()
    app.run()
    app.get_database().cursor.execute("SELECT * from Dogs")
    rows = app.get_database().fetchall()
    for row in rows:
        print("ID :", row[0])
        print("breed :", row[1])
        print("\n")
    app.get_database().close()


