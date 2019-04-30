"""
display_master.py

the master program for controling led ticker display. This program is
responsible for maintaining and running the web scrapers and initiating the
display loop
"""
import sports_scrapper as sports
import traffic_scrapper as traffic
import weather_scrapper as weather

import argparse
import threading
import datetime
import time
import random
import sys

"""
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
"""


PARSER = argparse.ArgumentParser()

PARSER.add_argument('-d', '--demo', action='store_true', default=False)

PARSER.add_argument('-p', '--pickled', action='store_true', default=False)
# indicate that the page should be cached for later
PARSER.add_argument('-c', '--cache', action='store_true', default=False)

WEATHER_INTERVAL = datetime.timedelta(minutes=30)
SPORTS_INTERVAL = datetime.timedelta(days=1)
TRAFFIC_INTERVAL = datetime.timedelta(minutes=20)
PHRASE_TIME = datetime.timedelta(minutes=3)

# may not implement these
DISPLAY_PHRASES = ['Tier 2 App Support FTW', 'We\'ll Handle it From here',
                   'Republic Services','Respectful','Responsible', 'Relentless', 'Reliable',
                   'Resourceful', 'FEED ME A CAT', 'HASTA LA VISTA',
                   'I\'LL BE BACK', 'Open the pod bay doors',
                   'I\'m sorry Dave, I\'m afraid I can\'t do that',
                   '<3 Isacc Asimov', 'Tier 2', 'R2-D2', 'Autobots, roll out!',
                   'It\'s over 9000!', 'The cake is a LIE']

class Demo():
    def __init__(self):
        """
        setup the rgb matrix; these options will be static for the demo
        """
        options = RGBMatrixOptions()

        options.rows = 16
        options.chain_length = 3
        options.parallel = 1
        options.pwm_bits = 11
        options.brightness = 50
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = 'RGB'

        self.matrix = RGBMatrix(options=options)

    def main(self, args: argparse.Namespace=None):
        """
        initiate display, and scraper threads and handle them appropriately
        """
        if args.demo:
            self.pickled = True
        else:
            self.pickled = args.pickled
            cache = args.cache

        try:
            # Start loop
            print("Press CTRL-C to stop demo")
            self.run()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

    def run(self, namespace=None):
        """
        main loop responsible for getting data and running it
        """

        demo_namespace = argparse.Namespace(pickled=True, cache=None, week=7, filename=None)
        sport_display = sports.main(demo_namespace)
        weather_display = weather.main(demo_namespace)
        traffic_display = sports.main(demo_namespace)

        sport_time = datetime.datetime.now()
        weather_time = sport_time
        traffic_time = sport_time


        outstring = self.generate_display_text(sport_display, weather_display, traffic_display)

        print(outstring)

        display_update = threading.Event()
        display_update.set()
        display_thread.join()

        display_thread = threading.Thread(target=self.display_text,
                                          kwargs={'text':outstring,
                                                  'event':display_update})
        display_thread.start()
        update = False

        while True:
            now = datetime.datetime.now()
            if now - sport_time > SPORTS_INTERVAL and not self.pickled:
                sport_display = sports.main(demo_namespace)
                update = True

            if now - weather_time > WEATHER_INTERVAL and not self.pickled:
                weather_display = weather.main(demo_namespace)
                update = True

            if now - traffic_time > TRAFFIC_INTERVAL and not self.pickled:
                traffic_display = sports.main(demo_namespace)
                update = True

            if update:
                outstring = self.generate_display_text(sport_display, weather_display,
                                                       traffic_display)
                display_update.clear()
                display_update.join()

                display_thread = threading.Thread(target=self.display_text,
                                                  kwargs={'text':outstring,
                                                          'event':display_update})
                display_thread.start()


    def generate_display_text(self, sport_display, weather_display, traffic_display):
        outstring = ''
        outstring = sport_display[0]+weather_display[0]+traffic_display[0]
        outstring += '    '
        outstring += DISPLAY_PHRASES[random.randrange(len(DISPLAY_PHRASES))]

        return outstring

    def display_text(self, text, event:threading.Event=None):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        # TODO make absolute
        font.LoadFont("../../../fonts/7x13.bdf")
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width
        my_text = self.args.text
        if event is None:
            while True:
                offscreen_canvas.Clear()
                len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
                pos -= 1
                if (pos + len < 0):
                    pos = offscreen_canvas.width

                time.sleep(0.05)
                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

        while True:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
            pos -= 1

            # reset display
            if pos + len < 0:
                pos = offscreen_canvas.width
                # only reset when the text is done scrolling
                if event.is_set():
                    return

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

if __name__ == '__main__':
    DEMO = Demo()
    args = PARSER.parse_args(sys.argv[1:])
    DEMO.main(args)
