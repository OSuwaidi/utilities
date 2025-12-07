# Embedded Programming

* What is Pulse-Width Modulation (PWM)?
  - It's a technique that enables digital output signal (e.g., voltage from microcontroller) to behave (interpreted) as an analog signal 
  for fine-grain control over peripherals by varying the digital signal's pulse width.
  - It switches between HIGH-LOW voltage signals very rapidly (pulses) such that the average voltage over time approximates an analog level to the load.
  - The period T is the time of **one full cycle** (time in secs between two consecutive rising edges).
  - The wave frequency is 1/T (Hz).
 
* What is a Duty Cycle?
- It's the fraction of time the voltage signal is HIGH during the entire period: (time signal is HIGH)/(total time) * 100%
- It determines the average output voltage:
  if HIGH was 5 V and the duty cycle was 25%, then the effective average voltage = 5 * 0.25 = 1.25 V
