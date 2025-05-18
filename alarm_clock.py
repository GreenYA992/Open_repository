import datetime
import threading
import time
import pygame

sounds = {
    '1': 'C:/Users/Green/Downloads/Кукла.mp3',
    '2': 'C:/Users/Green/Downloads/Лесник.mp3',
    '3': 'C:/Users/Green/Downloads/Молния.mp3'
}

class Notification:
    def notify(self):
        pass
class TextNotification(Notification):
    def notify(self):
        now = datetime.datetime.now()
        print(f'{now.strftime('%a - %H:%M')} Время вставать!')
        print('Введите "3", чтобы выключить: ')
class SoundNotification(Notification):
    def __init__(self, sound_file):
        self.sound_file = sound_file
    def notify(self):
        print('Звонок будильника!')
        print('Введите "3", чтобы выключить: ')
        pygame.mixer.music.load(self.sound_file)
        pygame.mixer.music.play()

class Alarm:
    def __init__(self, alarm_time, days, notification_type, repeat_interval, repeat=False):
        self.alarm_time = alarm_time
        self.days = days
        self.notification_type = notification_type
        self.repeat_interval = repeat_interval
        self.enabled = True
        self.repeat = repeat
    def set_repeat(self):
        self.repeat = True
    def should_ring(self):
        now = datetime.datetime.now()
        current_time = now.time()
        current_day = datetime.datetime.today().strftime('%a').upper()
        if not self.enabled or current_day not in self.days:
            return False
        if self.repeat:
            return self.alarm_time
        else:
            return current_time.hour == self.alarm_time.hour and current_time.minute == self.alarm_time.minute
    def disable(self):
        self.enabled = False
        self.repeat = False
        if isinstance(self.notification_type, SoundNotification):
            pygame.mixer.music.stop()
    def enable(self):
        self.enabled = True
    def __str__(self):
        return (f"Дни: {','.join(self.days)}, Время: {self.alarm_time}, "
                f"Уведомление: {'Звонок' if isinstance(self.notification_type, SoundNotification) else 'Беззвучный'}, "
                f"Активен? {'Да!' if self.enabled else 'Нет'}{', Повторяющийся' if self.repeat_interval else ''}")

class AlarmManager:
    def __init__(self):
        self.alarms = []
        self.rep_alarms = []
    def add_alarm(self, alarm):
        self.alarms.append(alarm)
    def print_alarms(self):
        if not self.alarms:
            print("Будильники отсутствуют.")
        else:
            print("Список установленных будильников:")
            for i, alarm in enumerate(self.alarms, start=1):
                print(f"{i}. {alarm}")
    def check_alarms(self):
        while True:
            now = datetime.datetime.now()
            x = now.strftime('%H:%M')
            for alarm in self.alarms:
                if x == '00:00':
                    alarm.enable()
                if alarm.should_ring():
                    alarm.notification_type.notify()
                    if alarm.repeat_interval is None:
                        alarm.disable()
                    else:
                        alarm.set_repeat()
                        time.sleep(float(alarm.repeat_interval) * 60)
            time.sleep(5)

class UserInterface:
    @staticmethod
    def get_alarm_input():
        try:
            time_input = input('Введите время будильника (HH:MM): ')
            alarm_time = datetime.datetime.strptime(time_input, '%H:%M').time()
            days = UserInterface._get_days_input()
            notification_type = UserInterface._get_notification_type()
            repeat_interval = int(input('Интервал повтора (минуты), введите 0, если повторять не надо: '))
            return Alarm(alarm_time, days, notification_type, repeat_interval if repeat_interval > 0 else None)
        except Exception as e:
            print(f'Произошла ошибка: {e}')
            return None
    @staticmethod
    def _get_days_input():
        while True:
            days_input = input('Введите дни недели (через запятую(", "), список: Mon,Tue,Wed,Thu,Fri,Sat,Sun): ').strip().upper()
            valid_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
            selected_days = days_input.split(', ')
            invalid_days = [d.strip() for d in selected_days if d.strip() not in valid_days]
            if len(invalid_days) > 0:
                print(f'Ошибка! Недействительные дни: {invalid_days}. Попробуйте снова.')
            else:
                break
        return selected_days
    @staticmethod
    def _get_notification_type():
        while True:
            note = input('Выберите тип уведомления (sound/text): ').upper()
            if note in ('SOUND', 'TEXT'):
                if note == 'SOUND':
                    sound_choice = input('Выберите звук (1, 2 или 3): ')
                    if sound_choice in sounds.keys():
                        sound_file = sounds.get(sound_choice)
                        print(f'Выбрана {sound_file}')
                        return SoundNotification(sound_file)
                    else:
                        print('Неверный ввод. Выберите звук (1, 2 или 3):.')
                else:
                    return TextNotification()
            else:
                print('Неверный ввод. Пожалуйста, выберите между "sound" и "text".')

def main():
    pygame.init()
    pygame.mixer.init()
    alarm_manager = AlarmManager()
    ui = UserInterface()
    thread = threading.Thread(target=alarm_manager.check_alarms, daemon=True)
    thread.start()
    #thread.join()
    while True:
        print('-----')
        print('-----')
        print('-----')
        print('1. Добавить будильник')
        print('2. Проверить будильники')
        print('3. Отключить будильник')
        print('4. Выход')
        print('Выберите действие: ')
        command = input()
        if command == '1':
            new_alarm = ui.get_alarm_input()
            if new_alarm:
                alarm_manager.add_alarm(new_alarm)
            else:
                continue
            print('Будильник установлен успешно.')
        elif command == '2':
            alarm_manager.print_alarms()
        elif command == '3':
            alarm_manager.off()
        elif command == '4':
            break
        else:
            print('Некорректная команда. Попробуйте снова.')

if __name__ == '__main__':
    main()
