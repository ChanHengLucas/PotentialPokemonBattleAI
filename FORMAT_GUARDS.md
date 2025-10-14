# Format Guards Documentation

This document summarizes which conditions are format-gated in the PokéAI system.

## Format Scoping

All services check the `format` parameter and gate Gen9OU-specific logic behind format checks.

### Current Format Support

- **gen9ou**: Full Gen 9 OU implementation
- **genXdummy**: Placeholder for testing (raises NotImplementedError)

### Service Boundary Guards

#### Calc Service (`/batch-calc`)
```python
if format != "gen9ou":
    raise NotImplementedError(f"Format {format} not supported")
```

**Gated Logic:**
- Type effectiveness calculations
- Weather/terrain damage modifiers
- Hazard damage calculations
- Status effect mechanics
- Priority and speed calculations
- Tera mechanics (when enabled)

#### Policy Service
```python
if format != "gen9ou":
    raise NotImplementedError(f"Format {format} not supported")
```

**Gated Logic:**
- Action space definition
- Legal action masking
- Tera action expansion (when enabled)
- Format-specific reward shaping

#### Teambuilder Service
```python
if format != "gen9ou":
    raise NotImplementedError(f"Format {format} not supported")
```

**Gated Logic:**
- Pokemon legality checks
- Move/ability/item restrictions
- Team composition validation
- Format-specific team generation

### Format-Specific Mechanics

#### Gen 9 OU Only
- **Tera mechanics**: Only when `format.tera_allowed == true`
- **Gen 9 abilities**: Intimidate, Regenerator, etc.
- **Gen 9 items**: Heavy-Duty Boots, Assault Vest, etc.
- **Gen 9 moves**: New moves and mechanics
- **Gen 9 clauses**: Sleep, Species, Evasion, OHKO, etc.

#### Format Gates by Category

##### Hazards
- **Stealth Rock**: Gen 9 OU only
- **Spikes**: Gen 9 OU only  
- **Toxic Spikes**: Gen 9 OU only
- **Sticky Web**: Gen 9 OU only
- **Heavy-Duty Boots**: Gen 9 OU only

##### Screens
- **Reflect/Light Screen**: Gen 9 OU only
- **Aurora Veil**: Gen 9 OU only (requires hail)
- **Infiltrator**: Gen 9 OU only

##### Weather
- **Sun/Rain/Sand/Hail**: Gen 9 OU only
- **Weather abilities**: Drought, Drizzle, Sand Stream, Snow Warning
- **Weather damage**: Gen 9 OU only

##### Terrain
- **Electric/Grassy/Misty/Psychic**: Gen 9 OU only
- **Terrain abilities**: Electric Surge, Grassy Surge, Misty Surge, Psychic Surge
- **Terrain effects**: Gen 9 OU only

##### Status Effects
- **Burn/Poison/Paralysis/Sleep/Freeze**: Gen 9 OU only
- **Confusion/Infatuation**: Gen 9 OU only
- **Status mechanics**: Gen 9 OU only

##### Abilities
- **Intimidate**: Gen 9 OU only
- **Regenerator**: Gen 9 OU only
- **Unaware**: Gen 9 OU only
- **Magic Guard**: Gen 9 OU only
- **Magic Bounce**: Gen 9 OU only
- **Good as Gold**: Gen 9 OU only

##### Items
- **Heavy-Duty Boots**: Gen 9 OU only
- **Assault Vest**: Gen 9 OU only
- **Choice items**: Gen 9 OU only
- **Life Orb**: Gen 9 OU only
- **Focus Sash**: Gen 9 OU only

##### Moves
- **Gen 9 moves**: Only in Gen 9 OU
- **Move mechanics**: Gen 9 OU only
- **Priority system**: Gen 9 OU only

##### Clauses
- **Sleep Clause**: Gen 9 OU only
- **Species Clause**: Gen 9 OU only
- **Evasion Clause**: Gen 9 OU only
- **OHKO Clause**: Gen 9 OU only
- **Moody Clause**: Gen 9 OU only
- **Swagger Clause**: Gen 9 OU only
- **Baton Pass Clause**: Gen 9 OU only

### Response Format

All services return format information in responses:

```json
{
  "format": "gen9ou",
  "format_version": "1.0.0",
  "dex_version": "gen9",
  "result": "..."
}
```

### Testing Format Guards

Use `tests/format/test_format_guards.py` to verify format gating:

```python
def test_non_gen9ou_format():
    """Test that non-gen9ou formats raise NotImplementedError"""
    with pytest.raises(NotImplementedError):
        calc_service.batch_calc(actions=[], format="genXdummy")
```

### Future Format Support

To add support for new formats:

1. Add format configuration to `config/formats/`
2. Update format guards in services
3. Add tests for new format
4. Update this documentation

### Format Versioning

Format configurations include version information for compatibility:

```yaml
format: "gen9ou"
version: "1.0.0"
dex_version: "gen9"
```

Services cache format configurations and include version in responses for debugging and compatibility checking.
