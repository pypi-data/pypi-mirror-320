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

/**
 * \brief fonction effectuant le pre-processing des donn�es
 * \param data Tableau de donn�es � transformer. Doit �tre de type UI16
 * \param nbInput Taille du tableau
 * \param preprocessed Tableau contenant les donn�es preprocess�es (doit �tre allou�)
 * \param mode Mode de transformation
 * \return Nombre de donn�es utiles dans le tableau transform�
 */
int preprocess(unsigned short* data,int nbInput,unsigned int* preprocessed,PreprocessMode mode);
/**
 * \brief Fonction effectuant la compression d'un bloc de donn�es
 * \param data Tableau de donn�es � compresser
 * \param nbInput Taille du tableau
 * \param compressed Tableau de retour pour les donn�es compress�es
 * \param compressedLen Taille du tableau de retour
 * \return la taille en octet du tableau compress� ou -1 en cas d'erreur
 */
int compress(unsigned int* data,int nbInput,unsigned char* compressed,int compressedLen);
/**@}*/ // End of group Exposed
