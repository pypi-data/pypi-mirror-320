#pragma once
/**********************************************************
 *					D�finition de la page de garde DOxygen
 **********************************************************/
/**
 * \mainpage Implementation de l'algorithme de compression de RICE du projet DESIR
 * \image html logo.jpg
 * \section Info Informations
 * \author Lo�c Gueguen
 * \version 1.0
 * \date
 * \section Description Description de la biblioth�que
 * Biblioth�que de compression et de d�compression bas�e sur l'agorithme de RICE du CCSDS (SZIP)
 * L'algorithme est adapt� aux s�pc�ficit�s du projet DESIR, � savoir:
 *	- Les pixels sont cod�s sur 16 bits
 *	- Le nombre de pixels est un multiple de 16
 */

/**********************************************************
 *					D�finition des sections DOxygen
 **********************************************************/
/**
 * \defgroup Exposed  Fonctions et types expos�s dans la DLL
 * \defgroup NotExposed  Fonctions et types non expos�s dans la DLL
 * \defgroup NotExposedCompressor  Fonctions et variables li�es � la compression
			* \ingroup NotExposed
 * \defgroup NotExposedUncompressor Fonctions et variables li�es � la decompression
			* \ingroup NotExposed
 * \defgroup Constantes  Constantes et macros pr�d�finies
 */


/**
 * \ingroup Exposed
* @{
*/
#include "GsrPreprocessMode.h"

int postprocessor(unsigned int* data,int nbInput,unsigned short* postProcessed,PreprocessMode mode);
/**
 * \brief Fonction effectuant la decompression d'un bloc de donn�es
 * \param compressed Tableau en entr�e contenant les donn�es compress�es
 * \param compressedLen Taille du tableau en entr�e
 * \param data Tableau de retour pour les donn�es d�compress�es.
 * \param nbInput Taille du tableau
 * \return nombre d'octets d�compress�s ou -1 en cas d'erreur
 */
int uncompress(unsigned char* compressed,int compressedLen,unsigned int* data,int nbInput);
/**@}*/ // End of group Exposed
