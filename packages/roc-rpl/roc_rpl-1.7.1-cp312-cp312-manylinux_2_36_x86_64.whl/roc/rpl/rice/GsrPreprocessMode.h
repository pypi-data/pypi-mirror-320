#pragma once
/**
 * \enum PreprocessMode
 * \brief D�crit les diff�rent algortihmes de preprocessing utilisables
 */
namespace Enumerations {
	typedef enum {
					ESTIMATE_1D_H, /**<One dimentional first order horizontal predictor \f$pre(x(i,j))=x(i-1,j)\f$*/
				}	PreprocessMode;
}

using namespace Enumerations;
