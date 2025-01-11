#pragma once
/**********************************************
 **************** Compression ***************** 
 **********************************************/
#pragma region Compressor functions
/**
* \ingroup NotExposedCompressor  Fonctions et variables li�es � la compression
* @{
*/
//Compressor variables
static int zero_blocks; /**< Nombre de zero_block cons�cutifs*/
static int newbits;
static unsigned long packed_bits; 
static unsigned long global_packed_bits;
static unsigned long packed_value;
static unsigned long global_packed_value;
static unsigned char *global_bptr;
static unsigned char *bptr;
static int nbBlock;

void initCompressor();
/**
 * \brief encodage de un ou plusieurs blocs "zero_bloc"
 * \param maxOrEnd La valeur 'true' indique que l'encodage est d�clench� en raison d'un nombre important de blocs (#MAX_ZERO_BLOCKS) ou de la fin de l'encoding
 */
void encodeZeroBlock(bool maxOrEnd);
/**
 * \brief encodage du MSB selon le principe des s�quences fondamentales
 * \param data Borne inf�rieur du bloc � encoder
 * \param end Borne sup�rieure (exclue) du bloc � encoder
 * \param lsbSize 
 */
void encodeMSB(unsigned int* data,unsigned int* end,int lsbSize);
/**
 * \brief encodage du LSB, cas Ksplit inclus dans [1,5]
 * \param data Borne inf�rieur du bloc � encoder
 * \param end Borne sup�rieure (exclue) du bloc � encoder
 * \param lsbSize 
 */
void encodeLSB(unsigned int* data,unsigned int* end,int lsbSize);
/**
 * \brief encodage du LSB, cas Ksplit inclus dans [6,8]
 * \param data Borne inf�rieur du bloc � encoder
 * \param end Borne sup�rieure (exclue) du bloc � encoder
 * \param lsbSize 
 */
void encodeLSBHO(unsigned int* data,unsigned int* end,int lsbSize);
/**
 * \brief Encodage du bloc de r�f�rence. Appel�e une seule fois pour le premier bloc
 * \param data Borne inf�rieur du bloc � encoder
 * \param end Borne sup�rieure (exclue) du bloc � encoder
 */
void encodeReferenceBlock(unsigned int* data,unsigned int* end);
/**
 * \brief Encodage d'un bloc quelconque.
 * \param data Borne inf�rieur du bloc � encoder
 * \param end Borne sup�rieure (exclue) du bloc � encoder
 * \param blockNro Indice du bloc (� partir de 1)
 */
void encodeNormalBlock(unsigned int* data, unsigned int* end,int blockNro);
/**
 * /brief vidage du tampon � la fin de la compression
 */
static void flush();  
/**
 * \brief recherche l'encodeur le plus performant pour un bloc de donn�es
 * \param sigma Borne inf�rieur du bloc � analyser 
 * \param end Borne sup�rieure (exclue) du bloc � analyser
 * \return r�f�rence de l'encodeur choisi (ID_ZERO, ID_LOW, ID_FS, ID_Kn)
 */
static int find_winner16(unsigned int *sigma, unsigned int *end);
/**
 * \brief recherche l'encodeur le plus performant pour le bloc de donn�es de r�f�rence
 * \param sigma Borne inf�rieur du bloc � analyser 
 * \param end Borne sup�rieure (exclue) du bloc � analyser
 * \return r�f�rence de l'encodeur choisi (ID_ZERO, ID_LOW, ID_FS, ID_Kn)
 */
static int find_ref_winner16(unsigned int *sigma, unsigned int *end);
/**
 * \brief Calcul le nombre de bits n�cessaires pour un encodage �tendu (ID_LOW)
 * \param sigma Borne inf�rieur du bloc � analyser 
 * \param end Borne sup�rieure (exclue) du bloc � analyser
 * \return 
 */
static unsigned int c_ext2(unsigned int* sigma, unsigned int* end);
/**@}*/ // End of group Compressor
#pragma endregion

/**********************************************
 **************** Decompression ****************
 **********************************************/
#pragma region Uncompressor functions
/**
* \ingroup NotExposedUncompressor 
* @{
*/
//Uncompressor variables
static int data_bits;
static unsigned int data_word;
static unsigned char *input_ptr;
#ifdef  GAUSS
static unsigned char *input_ptr_end;
#endif
static int leading_zeros[256];
void initUncompressor();
/**
* \brief fonction comptant le nombre de 0 cons�cutifs
* Cette fonction est utilis�e pour d�coder les encodages FS
* \return le nombre de 0 trouv�s	
*/
/**
 * \brief Decodage d'une s�quence fondamentale
 * \return Valeur d�cod�e
 */
int decodeFS();
/**
 * \brief d�codage de un ou plusieurs bloc de type 'Zero_Bloc'
 * \return Nombre de bloc de ce type d�cod�s
 */
int decodeZeroBlock();
/**
 * \brief d�codage du bloc de r�f�rence (la fonction n'est appel�e qu'un fois en d�but de d�compression)
 * \param data Borne inf�rieur du bloc destination � d�coder
 * \param end Borne sup�rieure (exclue) du bloc destination � d�coder
 * \return Nombre de bloc d�cod�s (1 dans le cas g�n�ral, plus dans le cas o� le bloc de r�f�rence est de type 'Zero_Bloc')
 */
int decodeReferenceBlock(unsigned int* data,unsigned int* end);
/**
 * \brief d�codage d'un bloc normal
 * \param data Borne inf�rieur du bloc destination � d�coder
 * \param end Borne sup�rieure (exclue) du bloc destination � d�coder
 * \param alreadyDecodedBlock Nombre de bloc d�j� d�cod�s
 * \return Nombre de nouveaux bloc s d�cod�s
 */
int decodeNormalBlock(unsigned int* data,unsigned int* end, int alreadyDecodedBlock);
/**
 * /brief Rempli le buffer de travail avec la suite des donn�es � d�coder
 */
static void fillDataBuffer();
/**@}*/ // End of group Uncompressor
#pragma endregion




