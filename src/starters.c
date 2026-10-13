#include "../include/constants/species.h"
#include "../include/pokemon.h"
#include "../include/types.h"
#include "../include/save.h"

extern u32 space_for_setmondata;
extern u32 sStarterChoiceCries[];

void LONG_CALL GetMonSpriteCharAndPlttNarcIdsEx(MON_PIC *picdata, u16 mons_no, u8 dir, u8 col, u8 form_no, u8 a5, u32 personality);

// Use MON_WITH_FORM(SPECIES_NAME, form) to specify a starter
// with a form.
//
// Keep in mind that these choices will impact Rival team
// determination in the appropriate trigger-scripts.
//
// This will NOT update the text during the starter-selection
// sequence. To update that text, modify text archive 190 in
// DSPRE.
// Script var holding the starter region the player picked: 1 = Kanto ... 9 = Paldea.
// Any other value (e.g. 0 before the region menu runs) falls back to Johto.
#define STARTER_REGION_VAR 0x40F9
#define NUM_STARTER_REGIONS 9

static const u16 sStarterChoicesByRegion[NUM_STARTER_REGIONS][3] = {
    { SPECIES_BULBASAUR,  SPECIES_CHARMANDER, SPECIES_SQUIRTLE },  // Kanto
    { SPECIES_CHIKORITA,  SPECIES_CYNDAQUIL,  SPECIES_TOTODILE },  // Johto
    { SPECIES_TREECKO,    SPECIES_TORCHIC,    SPECIES_MUDKIP },    // Hoenn
    { SPECIES_TURTWIG,    SPECIES_CHIMCHAR,   SPECIES_PIPLUP },    // Sinnoh
    { SPECIES_SNIVY,      SPECIES_TEPIG,      SPECIES_OSHAWOTT },  // Unova
    { SPECIES_CHESPIN,    SPECIES_FENNEKIN,   SPECIES_FROAKIE },   // Kalos
    { SPECIES_ROWLET,     SPECIES_LITTEN,     SPECIES_POPPLIO },   // Alola
    { SPECIES_GROOKEY,    SPECIES_SCORBUNNY,  SPECIES_SOBBLE },    // Galar
    { SPECIES_SPRIGATITO, SPECIES_FUECOCO,    SPECIES_QUAXLY },    // Paldea
};

static const u16 *GetStarterChoices(void)
{
    u16 region = GetScriptVar(STARTER_REGION_VAR);
    if (region < 1 || region > NUM_STARTER_REGIONS) {
        region = 2;
    }
    return sStarterChoicesByRegion[region - 1];
}

/**
 *  @brief fills the given array with the species ids of the starter choices
 *
 *  @param species pointer to the species array
 */
void LONG_CALL CreateStarter_SetStarterSpecies(int *species)
{
    for (int i = 0; i < 3; i++) {
        // strip off form
        species[i] = GetStarterChoices()[i] & 0x7FF;
    }
}

/**
 *  @brief wrap the CreateMon call within CreateStarter to allow for starter forms
 *
 *  @param mon the PartyPokemon pointer
 *  @param species the species id
 *  @param slot starter choice (0-2)
 */
void LONG_CALL CreateStarter_CreateMon(struct PartyPokemon *mon, int species, int slot)
{
    u32 form = 0;

    if (slot >= 0 && slot < 3) {
        form = GetStarterChoices()[slot] >> 11;
    }

    space_for_setmondata = form;
    PokeParaSet(mon, species, 5, 32, FALSE, 0, 0, 0);
    space_for_setmondata = 0;

    if (form != 0) {
        SetMonData(mon, MON_DATA_FORM, &form);
    }
}

/**
 *  @brief wrap the GetMonSpriteCharAndPlttNarcIdsEx call within createMonSprites to handle starter forms
 *
 *  @param pic MON_PIC pointer
 *  @param species species id
 */
void LONG_CALL CreateMonSprites_HandleForm(MON_PIC *pic, u16 species, u8 gender, u8 shiny, int slot)
{
    u32 form = 0;

    if (slot >= 0 && slot < 3) {
        form = GetStarterChoices()[slot] >> 11;
        sStarterChoiceCries[slot] = (form == 0) ? species : PokeOtherFormMonsNoGet(species, form);
    }

    GetMonSpriteCharAndPlttNarcIdsEx(pic, species, gender, 2, shiny, 0, 0);

    if (form != 0) {
        GetOtherFormPic(pic, species, 2, shiny, form);
    }
}
