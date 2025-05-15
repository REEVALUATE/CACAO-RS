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

We aggregate the rules as below, but add them individually to the rights statements, such that the resulting vocabulary terms are more expressive and easier to use. In addition, we can make minor changes automatically using the python script.

Unofficial definition of aggregating Rules:

```ttl
cacao_license:modify_permissions a odrl:Permission ;
    odrl:action odrl:aggregate ;
    odrl:action odrl:annotate ;
    odrl:action cc:DerivativeWorks ;
    odrl:action odrl:derive ;
    odrl:action odrl:modify ;
    odrl:action odrl:transform ;
    odrl:action odrl:translate ;

cacao_license:use_permissions a odrl:Permission ;
    odrl:action odrl:archive ;
    odrl:action odrl:concurrentUse ;
    odrl:action odrl:digitize ;
    odrl:action odrl:display ;
    odrl:action odrl:execute ;
    odrl:action odrl:extract ;
    odrl:action odrl:include ;
    odrl:action odrl:index ;
    odrl:action odrl:install ;
    odrl:action odrl:move ;
    odrl:action odrl:play ;
    odrl:action odrl:present ;
    odrl:action odrl:read ;
    odrl:action odrl:stream ;
    odrl:action odrl:synchronize ;
    odrl:action odrl:uninstall ;
    odrl:action odrl:delete ;
    odrl:action odrl:textToSpeech ;
    odrl:action odrl:print ;
    odrl:action odrl:reproduce ;
    odrl:action cc:Reproduction ;

cacao_license:commercial_permissions a odrl:Permission ;
    odrl:action cc:CommercialUse ;
    odrl:action odrl:sell ;

cacao_license:share_permissions a odrl:Permission ;
    odrl:action cc:Distribution ;
    odrl:action cc:Sharing ;
    odrl:action odrl:distribute ;


cacao_license:attribute_obligation a odrl:Duty ;
    odrl:action cc:Attribution ;
    odrl:action odrl:attribute ;
    odrl:action cc:Notice ;
    odrl:action odrl:inform ;
    .

cacao_license:change_license_prohibition a odrl:Prohibition ;
    odrl:action odrl:ensureExclusivity ;
    odrl:action odrl:grantUse ;
    odrl:action odrl:nextPolicy ;
    odrl:action odrl:watermark ;
    odrl:action odrl:reviewPolicy ;
    .
```