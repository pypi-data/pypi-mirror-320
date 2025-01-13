class Stopwatch {
  static #__get_time(){
    var nowTime = (new Date()).getTime();
    return nowTime / 1000 + ((nowTime % 1000) / 1000);
  }

  #__StartTime;

  constructor(){
    this.start();
  }

  start(){
    this.#__StartTime = Stopwatch.#__get_time();
  }

  stop(){
    return Stopwatch.#__get_time() - this.#__StartTime;
  }
}

module.exports = {
  Stopwatch: Stopwatch,
}
