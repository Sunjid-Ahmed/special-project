class Timeout:
    timeout = 0

    def set_timeout(self, timeout=6):
        self.timeout = timeout

    def reset_timeout(self):
        self.timeout = 0

    def is_timed_out(self):
        return self.timeout > 0

    def cycle_timout(self):
        if self.is_timed_out():
            self.timeout = self.timeout - 1


def main():
    pass


if __name__ == "__main__":
    main()
