;; Cooking task
;; Actions: scoop, flip, pour, fry, cut, join, stir, spray, transfer, blend, add, grab, sprinkle, wash, grate, squeegee
;; objs: 

(define (domain cooking)
	(:requirements :typing)
	(:types 
		container 
		obj 
		location
		cons-part
		spray)
		
	(:predicates
		(have ?x)
		(in ?x ?y)
		(on ?x ?y)
		(empty ?x)
		(isMixable ?x)
		(isHalfCooked ?x)
		(isFullCooked ?x)
		(atLoc ?x ?y)
		(isPourable ?x)
		(isSliceable ?x)
		(isSpatula ?x)
		(isScoop ?x)
		(isKnife ?x)
		(sprayed ?x)
		(mixed ?x)
		(isUtensil ?x)
		(isSliced ?x)
		(isBlender ?x)
		(isSmoothie ?x)
		(isIngredient ?x)
		(isAttached ?x ?y)
		(isGrated ?x)
		(haveScoop)
		(haveSpatula)
		
		(isDiff ?x ?y)
		
		(isSqueegee ?x)
		(isGrater ?x)
		(isClean ?x)
		(isWashed ?x)
		(isDirty ?x)
	)

	(:action flip
		:parameters (?x - obj ?y - container ?m - obj)
		:precondition (and
				(isSpatula ?m)
				(haveSpatula)
				(isUtensil ?y)
				(in ?x ?y)
				(isHalfCooked ?x))
		:effect (isFullCooked ?x)
	)			
	
	(:action grab
		:parameters (?x - obj ?l - location)
		:precondition (atLoc ?x ?l)
		:effect (and
				(have ?x)
				(not (atLoc ?x ?l)))
	)
	
	(:action pour
		:parameters (?x - obj ?y - container)
		:precondition (and 
				(isPourable ?x)
				(empty ?y)
				(have ?x))
		:effect (and
				(in ?x ?y)
				(not (empty ?y))
				(not (have ?x)))
	)
	
	(:action transfer
		:parameters (?x - obj ?y - container ?z - container)
		:precondition (and 
				(empty ?z)
				(in ?x ?y))
		:effect (and
				(empty ?y)
				(not (empty ?z))
				(in ?x ?z)
				(not (in ?x ?y)))
	)
	
	(:action stir
		:parameters (?x - obj ?y - container ?z - obj)
		:precondition (and
				(isScoop ?z)
				(in ?x ?y)
				(haveScoop)
				(isMixable ?y))
		:effect (mixed ?x)
	)			
	
	(:action spray
		:parameters (?y - container ?x - spray)
		:precondition (empty ?y)
		:effect (sprayed ?y)
	)
		
	(:action fry
		:parameters (?x - obj ?y - container)
		:precondition (and
				(mixed ?x)
				(sprayed ?y)
				(isUtensil ?y)
				(in ?x ?y))
		:effect (and
				(isHalfCooked ?x)
				(not (sprayed ?y)))
	)
	
	(:action cut
		:parameters (?x - obj ?y - obj)
		:precondition (and
			(isWashed ?x)
			(isKnife ?y)
			(isSliceable ?x)
			(have ?y)
			(have ?x))
		:effect (isSliced ?x)
	)
	
	(:action blend
		:parameters (?x - obj ?z - container)
		:precondition (and
				(isSliced ?x)
				(isBlender ?z)
				(in ?x ?z))
		:effect (isSmoothie ?x)
	)
	
	(:action add
		:parameters (?x - obj ?z - obj)
		:precondition (and
				(isIngredient ?x)
				(have ?x))
		:effect (in ?x ?z)
	)
	
	(:action scoop
		:parameters (?x - obj ?y - obj ?z - obj)
		:precondition (and
				(isIngredient ?x)
				(isScoop ?z)
				(haveScoop)
				(isSmoothie ?y)
				(have ?x))
		:effect (on ?x ?y)
	)
	
	(:action sprinkle
		:parameters (?x - obj ?y - obj)
		:precondition (and
				(isGrated ?x)
				(isFullCooked ?y)
				(have ?x))
		:effect (and 
				(on ?x ?y)
				(not (have ?x)))
	)
	
	(:action grate 
		:parameters (?x - obj ?y - obj)
		:precondition (and
				(have ?x)
				(have ?y)
				(isGrater ?y))
		:effect (isGrated ?x)
	)
	
	(:action wash
		:parameters (?x - obj)
		:precondition (and 
				(isDirty ?x))
		:effect (isWashed ?x)
	)
	
;; Attach action 
	
	(:action join-flip
		:parameters (?x - cons-part ?y - cons-part)
		:precondition (isDiff ?x ?y)
		:effect (haveSpatula)
	)
	
	(:action join-scoop
		:parameters (?x - cons-part ?y - cons-part)
		:precondition (isDiff ?x ?y)
		:effect (haveScoop)
	)
	
;; Irrelevant actions	
	
	(:action squeegee
		:parameters (?x - obj ?y - obj)
		:precondition (and
				(have ?y)
				(isDirty ?x)
				(isSqueegee ?y))
		:effect (isClean ?x)
	)
)