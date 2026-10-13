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
#define REGION_JOHTO 2

// Each region's grass, fire and water starter lines, first stage to last.
static const u16 sStarterFamilies[NUM_STARTER_REGIONS][3][3] = {
    { { SPECIES_BULBASAUR, SPECIES_IVYSAUR, SPECIES_VENUSAUR },               // Kanto
      { SPECIES_CHARMANDER, SPECIES_CHARMELEON, SPECIES_CHARIZARD },
      { SPECIES_SQUIRTLE, SPECIES_WARTORTLE, SPECIES_BLASTOISE } },
    { { SPECIES_CHIKORITA, SPECIES_BAYLEEF, SPECIES_MEGANIUM },               // Johto
      { SPECIES_CYNDAQUIL, SPECIES_QUILAVA, SPECIES_TYPHLOSION },
      { SPECIES_TOTODILE, SPECIES_CROCONAW, SPECIES_FERALIGATR } },
    { { SPECIES_TREECKO, SPECIES_GROVYLE, SPECIES_SCEPTILE },                 // Hoenn
      { SPECIES_TORCHIC, SPECIES_COMBUSKEN, SPECIES_BLAZIKEN },
      { SPECIES_MUDKIP, SPECIES_MARSHTOMP, SPECIES_SWAMPERT } },
    { { SPECIES_TURTWIG, SPECIES_GROTLE, SPECIES_TORTERRA },                  // Sinnoh
      { SPECIES_CHIMCHAR, SPECIES_MONFERNO, SPECIES_INFERNAPE },
      { SPECIES_PIPLUP, SPECIES_PRINPLUP, SPECIES_EMPOLEON } },
    { { SPECIES_SNIVY, SPECIES_SERVINE, SPECIES_SERPERIOR },                  // Unova
      { SPECIES_TEPIG, SPECIES_PIGNITE, SPECIES_EMBOAR },
      { SPECIES_OSHAWOTT, SPECIES_DEWOTT, SPECIES_SAMUROTT } },
    { { SPECIES_CHESPIN, SPECIES_QUILLADIN, SPECIES_CHESNAUGHT },             // Kalos
      { SPECIES_FENNEKIN, SPECIES_BRAIXEN, SPECIES_DELPHOX },
      { SPECIES_FROAKIE, SPECIES_FROGADIER, SPECIES_GRENINJA } },
    { { SPECIES_ROWLET, SPECIES_DARTRIX, SPECIES_DECIDUEYE },                 // Alola
      { SPECIES_LITTEN, SPECIES_TORRACAT, SPECIES_INCINEROAR },
      { SPECIES_POPPLIO, SPECIES_BRIONNE, SPECIES_PRIMARINA } },
    { { SPECIES_GROOKEY, SPECIES_THWACKEY, SPECIES_RILLABOOM },               // Galar
      { SPECIES_SCORBUNNY, SPECIES_RABOOT, SPECIES_CINDERACE },
      { SPECIES_SOBBLE, SPECIES_DRIZZILE, SPECIES_INTELEON } },
    { { SPECIES_SPRIGATITO, SPECIES_FLORAGATO, SPECIES_MEOWSCARADA },         // Paldea
      { SPECIES_FUECOCO, SPECIES_CROCALOR, SPECIES_SKELEDIRGE },
      { SPECIES_QUAXLY, SPECIES_QUAXWELL, SPECIES_QUAQUAVAL } },
};

static u16 GetStarterRegion(void)
{
    u16 region = GetScriptVar(STARTER_REGION_VAR);
    if (region < 1 || region > NUM_STARTER_REGIONS) {
        region = REGION_JOHTO;
    }
    return region - 1;
}

// first-stage starter in Poke Ball slot 0 (grass), 1 (fire) or 2 (water)
static u16 GetStarterChoice(int slot)
{
    return sStarterFamilies[GetStarterRegion()][slot][0];
}

/**
 *  @brief swap a Johto starter-line species for the same type and stage from the
 *         player's starter region, so the rival's team matches the region picked
 *
 *  @param species species to check (Chikorita through Feraligatr)
 *  @return the regional equivalent, or species unchanged if it isn't a Johto starter
 */
u16 LONG_CALL Starter_GetRegionalEquivalent(u16 species)
{
    for (int type = 0; type < 3; type++) {
        for (int stage = 0; stage < 3; stage++) {
            if (sStarterFamilies[REGION_JOHTO - 1][type][stage] == species) {
                return sStarterFamilies[GetStarterRegion()][type][stage];
            }
        }
    }
    return species;
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
        species[i] = GetStarterChoice(i) & 0x7FF;
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
        form = GetStarterChoice(slot) >> 11;
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
        form = GetStarterChoice(slot) >> 11;
        sStarterChoiceCries[slot] = (form == 0) ? species : PokeOtherFormMonsNoGet(species, form);
    }

    GetMonSpriteCharAndPlttNarcIdsEx(pic, species, gender, 2, shiny, 0, 0);

    if (form != 0) {
        GetOtherFormPic(pic, species, 2, shiny, form);
    }
}
