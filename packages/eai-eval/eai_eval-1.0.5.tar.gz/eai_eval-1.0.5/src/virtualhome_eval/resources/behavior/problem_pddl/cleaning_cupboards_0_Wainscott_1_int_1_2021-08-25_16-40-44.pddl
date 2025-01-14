(define (problem cleaning_cupboards)
    (:domain igibson)
    (:objects agent_n_01_1 - agent 
    bed_n_01_1 - bed_n_01 
    book_n_02_1 book_n_02_2 - book_n_02 
    bucket_n_01_1 - bucket_n_01 
    cabinet_n_01_1 cabinet_n_01_2 cabinet_n_01_3 - cabinet_n_01 
    pen_n_01_1 - pen_n_01 
    rag_n_01_1 - rag_n_01 
    screwdriver_n_01_1 - screwdriver_n_01 
    scrub_brush_n_01_1 - scrub_brush_n_01)
    (:init (dusty cabinet_n_01_2) 
    (inside book_n_02_1 cabinet_n_01_1) 
    (inside book_n_02_2 cabinet_n_01_2) 
    (inside pen_n_01_1 cabinet_n_01_1) 
    (inside rag_n_01_1 cabinet_n_01_1) 
    (inside scrub_brush_n_01_1 cabinet_n_01_1) 
    (ontop bucket_n_01_1 bed_n_01_1)
    (same_obj bed_n_01_1 bed_n_01_1) 
    (same_obj book_n_02_1 book_n_02_1) 
    (same_obj book_n_02_2 book_n_02_2) 
    (same_obj bucket_n_01_1 bucket_n_01_1) 
    (same_obj cabinet_n_01_1 cabinet_n_01_1) 
    (same_obj cabinet_n_01_2 cabinet_n_01_2) 
    (same_obj cabinet_n_01_3 cabinet_n_01_3) 
    (same_obj pen_n_01_1 pen_n_01_1) 
    (same_obj rag_n_01_1 rag_n_01_1)
    (same_obj screwdriver_n_01_1 screwdriver_n_01_1)
    (same_obj scrub_brush_n_01_1 scrub_brush_n_01_1))
    (:goal (and 
    (inside pen_n_01_1 bucket_n_01_1) 
    (not (dusty cabinet_n_01_2)) 
    (not (inside book_n_02_1 cabinet_n_01_2)) 
    (not (inside book_n_02_2 cabinet_n_01_3))))
)