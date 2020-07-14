;;Cleaning domain
;; Actions: wash, wipe, rake, fold, dry, grab, join, discard, pickup, store, dust, vacuum, hit, disinfect, clear, iron 

(define (domain cleaning)
	(:requirements :typing)
	(:types 
		surface
		obj
		location
		trash
		shelf
		smallObj
		cons-part
	)
	
	(:predicates
		(have ?x)
		(isClean ?x)
		(isDirty ?x)
		(isStowed ?x)
		(isWet ?x)
		(isRaked ?x)
		(atLoc ?x ?y)
		(isDry ?x)
		(isTrash ?x)
		(isFolded ?x)
		(isRakeable ?x)
		(isSmall ?x)
		(isVacuumed ?x)
		(isDisinfected ?x)
		(isMessy ?x)
		(isCleared ?x)
		(isIroned ?x)
		
		(isRake ?x)
		(isSqueegee ?x)
		(isRack ?x)
		(isIron ?x)
		(isDuster ?x)
		(isDisinfectant ?x)
		
		(isAttached ?x ?y)
		
		(isHammer ?x)
		(isHammered ?y)
		
		(haveRake)
		(haveSqueegee)
		(isDiff ?x ?y)
	)
	
	(:action wash
		:parameters (?x - obj)
		:precondition (and
				(isDirty ?x)
				(have ?x))
		:effect (and
				(isClean ?x)
				(isWet ?x))
	)
	
	(:action wipe
		:parameters (?x - surface ?y - obj)
		:precondition (and
				(haveSqueegee)
				(isDirty ?x)
				(isSqueegee ?y))
		:effect (isClean ?x)		
	)
	
	(:action collect
		:parameters (?x - obj ?y - obj)
		:precondition (and
				(haveRake)
				(isRake ?y)
				(isRakeable ?x))
		:effect (isRaked ?x)
	)
	
	(:action grab
		:parameters (?x - obj ?l - location)
		:precondition (atLoc ?x ?l)
		:effect (and
				(have ?x)
				(not (atLoc ?x ?l)))
	)
	
	(:action pickUp
		:parameters (?x - smallObj ?l - location)
		:precondition (atLoc ?x ?l)
		:effect (and
				(have ?x)
				(not (atLoc ?x ?l)))
	)
	
	(:action dry
		:parameters (?x - obj ?y - location)
		:precondition (and
				(isRack ?y)
				(have ?x)
				(isWet ?x))
		:effect (and
				(isDry ?x)
				(atLoc ?x ?y)
				(not (have ?x)))
	)
	
	(:action fold
		:parameters (?x - obj)
		:precondition (and
				(have ?x)
				(isIroned ?x))
		:effect (isFolded ?x)
	)
	
	(:action discard
		:parameters (?x - obj ?y - trash)
		:precondition (and
				(isTrash ?x)
				(have ?x))
		:effect (and
				(not (have ?x))
				(atLoc ?x ?y))
	)
	
	(:action dust
		:parameters (?x - smallObj ?y - obj)
		:precondition (and
				(isDuster ?y)
				(have ?x)
				(have ?y)
				(isDirty ?x))
		:effect (isClean ?x)
	)
	
	(:action store
		:parameters (?x - smallObj ?y - shelf)
		:precondition (and
				(have ?x)
				(isClean ?x))
		:effect (and
				(isStowed ?x)
				(not (have ?x)))
	)
	
	(:action vacuum
		:parameters (?x - surface)
		:precondition (isDirty ?x)
		:effect (isVacuumed ?x)
	)
	
	(:action disinfect
		:parameters (?x - surface ?y - obj)
		:precondition (and
				(isDisinfectant ?y)
				(have ?y)
				(isDirty ?x))
		:effect (and
				(isTrash ?y)
				(isDisinfected ?x))
	)
	
	(:action clear
		:parameters (?x - surface)
		:precondition (isMessy ?x)
		:effect (isCleared ?x)
	)
	
	(:action iron
		:parameters (?x - obj ?y - obj)
		:precondition (and
				(isIron ?y)
				(isDry ?x)
				(have ?x)
				(have ?y)
				(isClean ?x))
		:effect (isIroned ?x)
	)
	
	;; Attach action 
	
	(:action join-squeegee
		:parameters (?x - cons-part ?y - cons-part)
		:precondition (isDiff ?x ?y)
		:effect (haveSqueegee)
	)
	
	(:action join-rake
		:parameters (?x - cons-part ?y - cons-part)
		:precondition (isDiff ?x ?y)
		:effect (haveRake)
	)
	
	;; Irrelevant action
	
	(:action hit
		:parameters (?x - obj ?y - obj)
		:precondition (and
				(have ?y)
				(isHammer ?y))
		:effect (isHammered ?x)
	)
)