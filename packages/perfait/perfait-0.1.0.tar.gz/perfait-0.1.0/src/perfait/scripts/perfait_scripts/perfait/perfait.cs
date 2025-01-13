using System;

namespace Perfait {
  public class Stopwatch {
    private System.Diagnostics.Stopwatch m_Stopwatch;

    public Stopwatch(){
      m_Stopwatch = new System.Diagnostics.Stopwatch();
      Start();
    }

    public void Start(){
      m_Stopwatch.Reset();
      m_Stopwatch.Start();
    }

    public double Stop(){
      m_Stopwatch.Stop();
      return m_Stopwatch.Elapsed.TotalSeconds;
    }
  }
}
