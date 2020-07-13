(define (problem low)
(:domain nuclear)
 (:objects light1 UI1 user1 door1 buzzer1)
 (:init (light light1) (UI UI1) (user user1)(door door1)(buzzer buzzer1))
 (:goal (and (open door1) (ON UI1) (buzz buzzer1)))
)
 
