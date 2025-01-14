(define (problem sorting_mail_0)
    (:domain igibson)

    (:objects
        envelope.n.01_1 envelope.n.01_2 envelope.n.01_3 envelope.n.01_4 - envelope.n.01
        floor.n.01_1 - floor.n.01
        sofa.n.01_1 - sofa.n.01
        newspaper.n.03_1 newspaper.n.03_2 newspaper.n.03_3 newspaper.n.03_4 - newspaper.n.03
        agent.n.01_1 - agent.n.01
    )
    
    (:init 
        (onfloor envelope.n.01_1 floor.n.01_1) 
        (onfloor envelope.n.01_2 floor.n.01_1) 
        (onfloor envelope.n.01_3 floor.n.01_1) 
        (onfloor envelope.n.01_4 floor.n.01_1) 
        (onfloor newspaper.n.03_1 floor.n.01_1) 
        (onfloor newspaper.n.03_2 floor.n.01_1) 
        (onfloor newspaper.n.03_3 floor.n.01_1) 
        (onfloor newspaper.n.03_4 floor.n.01_1) 
        (inroom sofa.n.01_1 living_room) 
        (inroom floor.n.01_1 living_room) 
        (onfloor agent.n.01_1 floor.n.01_1)
    )
    
    (:goal 
        (and 
            (forall 
                (?envelope.n.01 - envelope.n.01) 
                (or 
                    (ontop ?envelope.n.01 ?envelope.n.01_1) 
                    (ontop ?envelope.n.01 ?envelope.n.01_2) 
                    (ontop ?envelope.n.01 ?envelope.n.01_3) 
                    (ontop ?envelope.n.01 ?envelope.n.01_4)
                )
            ) 
            (forall 
                (?newspaper.n.03 - newspaper.n.03) 
                (or 
                    (ontop ?newspaper.n.03 ?newspaper.n.03_1) 
                    (ontop ?newspaper.n.03 ?newspaper.n.03_2) 
                    (ontop ?newspaper.n.03 ?newspaper.n.03_3) 
                    (ontop ?newspaper.n.03 ?newspaper.n.03_4)
                )
            )
        )
    )
)