from datetime import datetime

class StopWatch:  # v2.1.0
    lap_timers = {}

    def __init__(self, trim=True, count=0):
        """
StopWatch is a simple timer utility. It's main intended use if for recording the run time for other processes.
        :param trim: (bool) Set to False if you want the decimals for the seconds
        :param count: (int) To set multiple concurrent timers, enter the number here, then you can call them
        individually using their 0 based index. If count is 0, a single timer called 'Start' will be started.
        """
        self.last_call = 'Start'
        self.trim = trim
        self.start_time = datetime.now()
        self.lap_timers[self.last_call] = self.start_time
        for i in range(count):
            self.lap_timers[i] = self.start_time
        self.__set_end()

    def __repr__(self):
        return str(datetime.now() - self.lap_timers['Start'])[:-7] if self.trim else \
            str(datetime.now() - self.lap_timers['Start'])

    def __set_end(self):
        self.end = str(datetime.now())[:-7] if self.trim else datetime.now()

    @property
    def start(self):
        return str(self.start_time)[:-7] if self.trim else str(self.start_time)

    @property
    def total(self):
        now_time = datetime.now() #
        out_str = str(self.start_time - now_time)
        if self.trim:
            out_str = out_str[:-7]
        return out_str

    # gets the time value of the timer[name]
    def get(self, name='Start'):
        """
Gets the time elapsed since the last check_lap (or the StopWatch was instantiated).
        :param name: (str or int) The name of the timer being queried.
        :return: (str) Elapsed time in the format: h:mm:ss[.dddddd]
        """
        if name == 'LastCall':
            name = self.last_call
        # self.last_call = name
        out_time = datetime.now() - self.lap_timers[name]
        self.__set_end()
        return out_time

    def check_lap(self, name='Start'):
        """
Check time interval since timer 'name' was last checked (or started). Using check_lap will effectively reset the start
each time. In this case, you can still get the time since start by using StopWatch.total.
If you wish to be able to continue to use the get() function for returning the total time, set name to something other 
than 'Start'.
        :param name: (str or int) Name of the timer being checked. If not specified, will default to the 'Start' timer.
        Passing 'LastCall' will select the name of the last timer that was checked or reset.
        :return: (str format: h:mm:ss[.dddddd]) The time since the last lap check.
        """
        if name == 'LastCall':
            name = self.last_call
        self.last_call = name
        now_time = datetime.now()
        if name in self.lap_timers:
            out_str = str(now_time - self.lap_timers[name])
        else:
            out_str = str(now_time - self.lap_timers['Start'])
        self.lap_timers[name] = now_time
        if self.trim:
            out_str = out_str[:-7]
        self.__set_end()
        return out_str

    def interval(self, end, name='Start'):
        """
Check the time elapsed between the end timer and the start timer, (defaults to 'Start').
        :param end: (str/int) The name of the timer being used as the end point
        :param name: (str/int) The name of the timer being used as the start point (Defaults to 'Start'). Passing 'LastCall' will select the name of the last timer that was checked or reset.
        :return: (str) Elapsed time in the format: h:mm:ss[.dddddd]
        """
        if name == 'LastCall':
            name = self.last_call
        self.last_call = name
        if end in self.lap_timers:
            out_str = str(self.lap_timers[end] - self.lap_timers[name])
        else:
            self.lap_reset(end)
            out_str = str(datetime.now() - self.lap_timers[name])
        if self.trim:
            out_str = out_str[:-7]
        self.__set_end()
        return out_str

    def lap_reset(self, name, time_now='Now'):
        """
Check time interval since timer 'name' was last checked, reset or started. Using lap_reset (rather than check_lap) 
allows you to specify both a start and an end point. For example: After calling check_lap('Lap'), at a later stage, 
calling lap_reset('Start', time_now='Lap') would return the time elapsed between the 'Start' timer and the 'Lap' timer,
then set the 'Start' timer to the value of the 'Lap' timer.
You can still get the total time elapsed for the 'Start' timer by using StopWatch.total.
If you wish to be able to continue to use the get() function for returning the total time, set name to something other 
than 'Start'.
        :param name: (str or int) The name of the timer being reset. (You cannot reset the 'Start' timer)
        Passing 'LastCall' will select the name of the last timer that was checked or reset.
        :param time_now: (str/int) If the name (or index) time_now
        :return: (str) Elapsed time in the format: h:mm:ss[.dddddd]
        """
        if name == 'LastCall':
            name = self.last_call
        self.last_call = name
        if name == 'Start':
            return "Error: Cannot reset Start time!"
        now_time = self.lap_timers[time_now] if time_now in self.lap_timers else datetime.now()
        if name in self.lap_timers:
            out_str = str(now_time - self.lap_timers[name])
        else:
            out_str = str(now_time - self.lap_timers['Start'])
        self.lap_timers[name] = now_time
        if self.trim:
            out_str = out_str[:-7]
        self.__set_end()
        return out_str

    def list(self):
        """
Provides a dict containing all the timers generated in this StopWatch.
        :return: (dict)
        """
        out_list = {}
        time_now = datetime.now()
        timer_id = 0
        for timer in self.lap_timers:
            out_str = str(time_now - self.lap_timers[timer])
            if self.trim:
                out_str = out_str[:-7]
            out_list[timer] = out_str
            timer_id += 1
        return out_list

    def now(self, as_str=True):
        """
Simply returns the current date and time. Generally used for a quick string conversion of the datetime.now() function
        :param as_str: (bool) Setting to false provides the datetime.now() output.
        :return: (str or datetime) The current date and time
        """
        out_time = datetime.now()
        out_str = str(out_time)[:-7] if self.trim else str(out_time)
        return out_str if as_str else out_time


