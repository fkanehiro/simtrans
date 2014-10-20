from pyparsing import *

def vrmlgrammer():
    '''
    Parser for VRML definition

    >>> p = vrmlgrammer()
    >>> p.parseString("""
PROTO Segment [
    field           SFVec3f     bboxCenter        0 0 0
    field           SFVec3f     bboxSize          -1 -1 -1
    exposedField    SFVec3f     centerOfMass      0 0 0
    exposedField    MFNode      children          [ ]
    exposedField    SFNode      coord             NULL
    exposedField    MFNode      displacers        [ ]
    exposedField    SFFloat     mass              0
    exposedField    MFFloat     momentsOfInertia  [ 0 0 0 0 0 0 0 0 0 ]
    exposedField    SFString    name              ""
    eventIn         MFNode      addChildren
    eventIn         MFNode      removeChildren
]
{
    Group {
        addChildren    IS addChildren
        bboxCenter     IS bboxCenter
        bboxSize       IS bboxSize
        children       IS children
        removeChildren IS removeChildren
    }
}
""")
    >>> p.parseString("""
# this is a comment
DEF HRP1 Humanoid {
  humanoidBody [
    DEF BASE Joint {
      jointType "fixed"
      translation 0.0 0.0 0.0
      rotation 0 0 1 0
      children [
        DEF BASE_LINK Segment {
	  mass 3.04
          centerOfMass 0 0 0.075
	  momentsOfInertia [1 0 0 0 1 0 0 0 1]
          children [
             Inline {
                url "base.wrl"
             }
            #-----------------------------------------#
          ]
        }
        DEF J1 Joint {
          jointType "rotate"
          jointAxis 0 0 1
          jointId 0
          translation 0 0 0.2
          rotation 0 0 1 0
          ulimit 3.08923278
          llimit -3.08923278
          rotorInertia 3.0E-4
          children [
            DEF J1_LINK Segment {
              mass 9.78
              centerOfMass 0 0 0.14818
              momentsOfInertia [1 0 0 0 1 0 0 0 1]
              children [
                Inline {
                  url "j1.wrl"
                }
              ]
            }
          ]
        } # end of joint J1
      ]
    } # end of joint BASE
  ]
  joints [
    USE BASE,
    USE J1
  ]
  segments [
    USE BASE_LINK,
    USE J1_LINK
  ]
  name "pa10"
  version "1.1"
}
""")
    '''
    lbrace = Literal("{")
    rbrace = Literal("}")
    lbrack = Literal("[")
    rbrack = Literal("]")
    comma = Literal(",")
    proto_ = Keyword("PROTO")
    DEF_ = Keyword("DEF")
    children_ = Keyword("children")
    group_ = Keyword("Group")
    transform_ = Keyword("Transform")
    is_ = Keyword("IS")
    comment = "#" + restOfLine
