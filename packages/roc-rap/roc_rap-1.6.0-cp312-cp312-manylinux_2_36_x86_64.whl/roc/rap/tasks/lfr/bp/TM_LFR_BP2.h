#ifndef TM_LFR_BP2_H
#define TM_LFR_BP2_H

#include "TM_LFRScienceReader.h"

using namespace std;

//CONSTRUCTOR
class TM_LFR_BP2 : public TM_LFRScienceReader
{
protected :
    int dataLength;
    uint16_t rawFloat;
    uint8_t A_exp;
    uint16_t A_sig;
    int exp;
    double sig;
    // For floating point data to be recorded on 16-bit words : (from basic_parameter.h in FSW)
    uint8_t nbitexp;                    // 8-bit unsigned integer
    uint8_t nbitsig;
    int8_t expmin;                      // 8-bit signed integer
    int8_t expmax;
    uint16_t rangesig;

public :
    //Constructor
    TM_LFR_BP2(ifstream & binSrc,struct pktHeaderVar & hdrStruct, string outName, string mode, string frq);

    //Methods
    void dumpPktToAscii();

    double convToAutoFloat(uint16_t rFloat);
    float convToCrossFloat(uint8_t rUint);
};

#endif // TM_LFR_BP2_H
