(define (problem low)
(:domain nuclear)
 (:objects light1 buzzer1)
 (:init (OrangeLED light1) (buzzerMid buzzer1))
 (:goal (and (turned light1)(buzz buzzer1)))
)
 
