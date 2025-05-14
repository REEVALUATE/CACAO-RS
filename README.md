# CACAO-RS

## Mapping strategy

Full use of the artefact 

Based on Actions for Rules: https://www.w3.org/TR/odrl-vocab/#actions and https://www.w3.org/TR/odrl-vocab/#actionsCommon


Aggregating actions:
- use
- transfer ownership


odrl:use contains all of the following:
- cc:Attribution
- cc:CommercialUse (there is a typo in the official docs? it says CommericalUse)
- cc:DerivativeWorks
- cc:Distribution
- cc:Notice
- cc:Reproduction
- cc:ShareAlike
- cc:Sharing
- cc:SourceCode
- odrl:acceptTracking
- odrl:aggregate
- odrl:annotate
- odrl:anonymize
- odrl:archive
- odrl:attribute
- odrl:compensate
- odrl:concurrentUse
- odrl:delete
- odrl:derive
- odrl:digitize
- odrl:distribute
- odrl:ensureExclusivity
- odrl:execute
- odrl:grantUse
- odrl:include
- odrl:index
- odrl:inform
- odrl:install
- odrl:modify
- odrl:move
- odrl:nextPolicy
- odrl:obtainConsent
- odrl:play
- odrl:present
- odrl:print
- odrl:read
- odrl:reproduce
- odrl:reviewPolicy
- odrl:stream
- odrl:synchronize
- odrl:textToSpeech
- odrl:transform
- odrl:translate
- odrl:uninstall
- odrl:watermark

odrl:transfer includes all of the following:
- odrl:give
- odrl:sell

permission and prohibition should be mutually exclusive

prohibition and duty should be mututally exclusve

permission and duty can overlap, in fact do you need the permission to perform the duty? -> they SHOULD overlap

Can we minimize to the ones where we are absolutely sure? Instead of using all of them?

## Strategy

Some actions do not make much sense with certain Rules, so:
- Permission:
  - accept tracking
  - aggregate
  - annotate
  - anonymize
  - archive
  - attribute (duty)
  - attribution (duty)
  - commercialuse
  - compensate (duty)
  - concurrent use (duty)
  - delete (duty)
  - derive 
  - derivative works
  - digitize
  - display
  - distribute
  - distribution
  - ensure exclusivity (duty?)
  - execute
  - extract
  - give (deletion of original asset?!)
  - grant use

https://github.com/Daham-Mustaf/LLM4ODRL/tree/main
https://vldb.org/workshops/2024/proceedings/LLM+KG/LLM+KG-15.pdf#page=2.88

