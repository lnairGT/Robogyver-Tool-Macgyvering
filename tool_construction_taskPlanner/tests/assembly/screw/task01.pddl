; woodworking task with 3 parts and 140% wood
; Machines:
;   1 grinder
;   1 glazer
;   1 immersion-varnisher
;   1 planer
;   1 highspeed-saw
;   1 spray-varnisher
;   1 saw
; random seed: 854322

(define (problem wood-prob)
  (:domain woodworking)
  (:objects
	hammer screwdriver - tool
    grinder0 - grinder
    glazer0 - glazer
    immersion-varnisher0 - immersion-varnisher
    planer0 - planer
    highspeed-saw0 - highspeed-saw
    spray-varnisher0 - spray-varnisher
    saw0 - saw
    green mauve - acolour
    cherry beech - awood
    p0 p1 p2 - part
    b0 b1 - board
    s0 s1 s2 s3 - aboardsize
	obj0 obj1 obj2 obj3 obj4 obj5 obj6 obj7 obj8 obj9 - cons-part
  )
  
  (:init
    (grind-treatment-change varnished colourfragments)
    (grind-treatment-change glazed untreated)
    (grind-treatment-change untreated untreated)
    (grind-treatment-change colourfragments untreated)
    (is-smooth smooth)
    (is-smooth verysmooth)
    
    (boardsize-successor s0 s1)
    (boardsize-successor s1 s2)
    (boardsize-successor s2 s3)
    (has-colour glazer0 mauve)
    (has-colour glazer0 green)
    (has-colour immersion-varnisher0 mauve)
    (empty highspeed-saw0)
    (has-colour spray-varnisher0 mauve)
    (unused p0)
    (goalsize p0 medium)
    
    
    
    
    (unused p1)
    (goalsize p1 medium)
    
    
    
    
    (available p2)
    (colour p2 natural)
    (wood p2 beech)
    (surface-condition p2 verysmooth)
    (treatment p2 colourfragments)
    (goalsize p2 small)
    
    
    
    
    (boardsize b0 s3)
    (wood b0 beech)
    (surface-condition b0 rough)
    (available b0)
    (boardsize b1 s3)
    (wood b1 cherry)
    (surface-condition b1 rough)
    (available b1)
	
	(isHammer hammer)
	(isScrewdriver screwdriver)
	(haveHammer)
		
	(isDiff obj1 obj2)
	(isDiff obj1 obj3)
	(isDiff obj1 obj4)
	(isDiff obj1 obj5)
	(isDiff obj1 obj6)
	(isDiff obj1 obj7)
	(isDiff obj1 obj8)
	(isDiff obj1 obj9)
	(isDiff obj1 obj0)
		
	(isDiff obj2 obj1)
	(isDiff obj2 obj3)
	(isDiff obj2 obj4)
	(isDiff obj2 obj5)
	(isDiff obj2 obj6)
	(isDiff obj2 obj7)
	(isDiff obj2 obj8)
	(isDiff obj2 obj9)
	(isDiff obj2 obj0)
		
	(isDiff obj3 obj2)
	(isDiff obj3 obj1)
	(isDiff obj3 obj4)
	(isDiff obj3 obj5)
	(isDiff obj3 obj6)
	(isDiff obj3 obj7)
	(isDiff obj3 obj8)
	(isDiff obj3 obj9)
	(isDiff obj3 obj0)
		
	(isDiff obj4 obj2)
	(isDiff obj4 obj3)
	(isDiff obj4 obj1)
	(isDiff obj4 obj5)
	(isDiff obj4 obj6)
	(isDiff obj4 obj7)
	(isDiff obj4 obj8)
	(isDiff obj4 obj9)
	(isDiff obj4 obj0)
		
	(isDiff obj5 obj2)
	(isDiff obj5 obj3)
	(isDiff obj5 obj4)
	(isDiff obj5 obj1)
	(isDiff obj5 obj6)
	(isDiff obj5 obj7)
	(isDiff obj5 obj8)
	(isDiff obj5 obj9)
	(isDiff obj5 obj0)
	
	(isDiff obj6 obj2)
	(isDiff obj6 obj3)
	(isDiff obj6 obj4)
	(isDiff obj6 obj5)
	(isDiff obj6 obj1)
	(isDiff obj6 obj7)
	(isDiff obj6 obj8)
	(isDiff obj6 obj9)
	(isDiff obj6 obj0)
		
	(isDiff obj7 obj2)
	(isDiff obj7 obj3)
	(isDiff obj7 obj4)
	(isDiff obj7 obj5)
	(isDiff obj7 obj6)
	(isDiff obj7 obj1)
	(isDiff obj7 obj8)
	(isDiff obj7 obj9)
	(isDiff obj7 obj0)
		
	(isDiff obj8 obj2)
	(isDiff obj8 obj3)
	(isDiff obj8 obj4)
	(isDiff obj8 obj5)
	(isDiff obj8 obj6)
	(isDiff obj8 obj7)
	(isDiff obj8 obj1)
	(isDiff obj8 obj9)
	(isDiff obj8 obj0)
		
	(isDiff obj9 obj2)
	(isDiff obj9 obj3)
	(isDiff obj9 obj4)
	(isDiff obj9 obj5)
	(isDiff obj9 obj6)
	(isDiff obj9 obj7)
	(isDiff obj9 obj8)
	(isDiff obj9 obj1)
	(isDiff obj9 obj0)
		
	(isDiff obj0 obj2)
	(isDiff obj0 obj3)
	(isDiff obj0 obj4)
	(isDiff obj0 obj5)
	(isDiff obj0 obj6)
	(isDiff obj0 obj7)
	(isDiff obj0 obj8)
	(isDiff obj0 obj9)
	(isDiff obj0 obj1)	
  )
  
  (:goal
    (and
      (available p0)
      ;;(colour p0 mauve)
      (wood p0 beech)
      (surface-condition p0 verysmooth)
      (treatment p0 varnished)
      (available p1)
      ;;(colour p1 green)
      (wood p1 cherry)
      (surface-condition p1 smooth)
      (treatment p1 glazed)
      (available p2)
      ;;(colour p2 mauve)
      (wood p2 beech)
	  (isHammered p0)
	  (isHammered p1)
	  (isTight p0 p1)
    )
  )
  
)
