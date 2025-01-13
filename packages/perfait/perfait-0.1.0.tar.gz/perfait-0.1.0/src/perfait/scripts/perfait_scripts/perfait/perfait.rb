module Perfait
  class Stopwatch
    def self.__get_time
      return Time.now().to_f
    end

    def initialize
      start()
    end

    def start
      @__StartTime = Stopwatch.__get_time()
    end

    def stop
      Stopwatch.__get_time() - @__StartTime
    end
  end
end
