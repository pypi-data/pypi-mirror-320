#ifndef TM_LFR_BP1_H
#define TM_LFR_BP1_H

#include "TM_LFRScienceReader.h"

using namespace std;

//CONSTRUCTOR
class TM_LFR_BP1 : public TM_LFRScienceReader
{
protected :
    int dataLength;
    bool hasSpare26;
    uint8_t SX_sign;
    uint8_t SX_arg;
    uint8_t VPHI_sign;
    uint8_t VPHI_arg;
    double SX;
    double VPHI;
    uint8_t NVEC_V2_sign;
    float NVEC_V0;
    float NVEC_V1;
    float NVEC_V2;
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
    uint16_t rangesig_16;
    uint16_t rangesig_14;

public :
    //Constructor
    TM_LFR_BP1(ifstream & binSrc,struct pktHeaderVar & hdrStruct, string outName, string mode, string frq);

    //Methods
    void dumpPktToAscii();

    double convToFloat16(uint16_t rFloat);
    float convToFloat8(uint8_t rUint);
    float convToFloat4(uint8_t rUint);
    float convToFloat3(uint8_t rUint);
    double convToFloat14(uint16_t rFloat);

};

#endif // TM_LFR_BP1_H
