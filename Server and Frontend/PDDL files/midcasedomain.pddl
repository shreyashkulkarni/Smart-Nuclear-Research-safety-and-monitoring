(define (domain nuclear)
    (:predicates
      (OrangeLED ?l)
      (turned ?l)
	  
      (buzzerMid ?b)
	  (buzz ?b)
    )
    (:action turnonOrange
      :parameters (?l ?b)
      :precondition (and (OrangeLED ?l) (not(turned ?l))(buzzerMid ?b)(not(buzz ?b)))
      :effect (turned ?l)
    )
    (:action turn-off-OrangeLED
      :parameters (?l ?b)
      :precondition (and (OrangeLED ?l) (turned ?l)(buzzerMid ?b)(buzz ?b))
      :effect (not (turned ?l))
    )
   
   
   (:action buzzer-ON
      :parameters (?b ?d ?l)
      :precondition (and (buzzerMid ?b)(not(buzz ?b)) (OrangeLED ?l)(turned ?l))
      :effect (buzz ?b)
   )
	(:action buzzer-off
      :parameters (?b  ?l)
      :precondition (and (buzzerMid ?b)(buzz ?b) (OrangeLED ?l)(not(turned ?l)))
      :effect (not(buzz ?b))
    )
   
)             

 
