(function () {
  const root = window.MealsOnWheels || (window.MealsOnWheels = {});

  const pitStops = [
    {
      id: "petworth",
      name: "Petworth Family Hub",
      short: "Petworth",
      shortLabel: "Petworth",
      lat: 38.9418,
      lng: -77.0242,
      area: "Petworth, Brightwood, 16th Street Heights, and nearby households",
      zip: "20011",
      zips: ["20011", "20012"],
      type: "Resident pickup and locker bank",
      stockBoost: 1.07,
      priority: 1,
      services: ["Residents first", "Locker pickup", "Support boxes"],
      note: "Northwest resident hub with subsidy-ready pickup."
    },
    {
      id: "columbia_heights",
      name: "Columbia Heights Market Hub",
      short: "Columbia Heights",
      shortLabel: "Columbia Hts",
      lat: 38.9287,
      lng: -77.0322,
      area: "Columbia Heights, Park View, and Adams Morgan edge",
      zip: "20010",
      zips: ["20009", "20010"],
      type: "Fresh pickup and apartment lockers",
      stockBoost: 1.05,
      priority: 2,
      services: ["Residents first", "Fresh produce", "Apartment pickup"],
      note: "Dense household coverage west of Georgia Avenue."
    },
    {
      id: "logan_shaw",
      name: "Logan Shaw Resident Hub",
      short: "Logan / Shaw",
      shortLabel: "Logan",
      lat: 38.9099,
      lng: -77.0299,
      area: "Shaw, Logan Circle, mixed-income buildings, and downtown residences",
      zip: "20001",
      zips: ["20001", "20005", "20006", "20036", "20037"],
      type: "Resident pickup and rapid restock",
      stockBoost: 1.03,
      priority: 3,
      services: ["Residents first", "Rapid restock", "Campus add-on"],
      note: "Central resident hub without relying on a monument-area stop."
    },
    {
      id: "georgetown_palisades",
      name: "Georgetown Palisades Hub",
      short: "Georgetown",
      shortLabel: "Georgetown",
      lat: 38.915,
      lng: -77.0724,
      area: "Georgetown, Burleith, Glover Park, and Palisades",
      zip: "20007",
      zips: ["20007", "20057"],
      type: "Neighborhood locker pickup",
      stockBoost: 0.99,
      priority: 4,
      services: ["Residents first", "Senior access", "Campus add-on"],
      note: "West-side resident coverage with campus access as an add-on."
    },
    {
      id: "tenley_chevy",
      name: "Tenley Chevy Chase Hub",
      short: "Tenley / Chevy",
      shortLabel: "Tenley",
      lat: 38.946,
      lng: -77.0775,
      area: "Tenleytown, Chevy Chase, Friendship Heights, and upper Ward 3 homes",
      zip: "20016",
      zips: ["20008", "20015", "20016"],
      type: "Uptown household pickup",
      stockBoost: 0.98,
      priority: 5,
      services: ["Residents first", "Apartment pickup", "Campus add-on"],
      note: "Uptown household pickup with campus overflow support."
    },
    {
      id: "brookland_edgewood",
      name: "Brookland Edgewood Hub",
      short: "Brookland",
      shortLabel: "Brookland",
      lat: 38.9325,
      lng: -76.9958,
      area: "Brookland, Edgewood, Michigan Park, and nearby family housing",
      zip: "20017",
      zips: ["20017", "20018", "20064"],
      type: "Resident pickup and locker blend",
      stockBoost: 1.06,
      priority: 6,
      services: ["Residents first", "Locker pickup", "Campus add-on"],
      note: "Northeast household coverage with student pickup secondary."
    },
    {
      id: "capitol_east",
      name: "Capitol East Resident Hub",
      short: "Capitol East",
      shortLabel: "Capitol East",
      lat: 38.8896,
      lng: -76.9894,
      area: "Capitol Hill East, Hill East, H Street corridor, and nearby apartments",
      zip: "20003",
      zips: ["20002", "20003"],
      type: "Resident pickup and route staging",
      stockBoost: 1.02,
      priority: 7,
      services: ["Residents first", "Fresh pickup", "Support boxes"],
      note: "East-central staging hub for repeat resident pickup."
    },
    {
      id: "southwest_wharf",
      name: "Southwest Wharf Hub",
      short: "Southwest",
      shortLabel: "Southwest",
      lat: 38.8768,
      lng: -77.0243,
      area: "Southwest Waterfront, Wharf residences, and nearby senior buildings",
      zip: "20024",
      zips: ["20004", "20024"],
      type: "Resident locker and short-hop delivery",
      stockBoost: 1.01,
      priority: 8,
      services: ["Residents first", "Senior access", "Short-hop delivery"],
      note: "Southwest household hub serving residents rather than the monument core."
    },
    {
      id: "deanwood_benning",
      name: "Deanwood Benning Hub",
      short: "Deanwood",
      shortLabel: "Deanwood",
      lat: 38.8894,
      lng: -76.9488,
      area: "Deanwood, Benning, Marshall Heights, and east Ward 7 households",
      zip: "20019",
      zips: ["20019"],
      type: "East-of-river fresh pickup",
      stockBoost: 1.09,
      priority: 9,
      services: ["Residents first", "Fresh pickup", "Subsidized pricing"],
      note: "East-of-river coverage centered on household affordability."
    },
    {
      id: "anacostia_skyland",
      name: "Anacostia Skyland Hub",
      short: "Anacostia",
      shortLabel: "Anacostia",
      lat: 38.8625,
      lng: -76.9802,
      area: "Anacostia, Fairlawn, Skyland, and surrounding residences",
      zip: "20020",
      zips: ["20020"],
      type: "Family box distribution and pickup",
      stockBoost: 1.11,
      priority: 10,
      services: ["Residents first", "Family boxes", "Locker pickup"],
      note: "High-priority resident hub for family pickup and support boxes."
    },
    {
      id: "congress_heights",
      name: "Congress Heights South Hub",
      short: "Congress Heights",
      shortLabel: "Congress Hts",
      lat: 38.8445,
      lng: -76.9925,
      area: "Congress Heights, Bellevue, and Washington Highlands",
      zip: "20032",
      zips: ["20032"],
      type: "South DC pickup and support route",
      stockBoost: 1.12,
      priority: 11,
      services: ["Residents first", "Support boxes", "Short-hop delivery"],
      note: "South DC resident hub with strong subsidy focus."
    }
  ];

  const residentZipAreas = [
    { zip: "20001", label: "Shaw / Mount Vernon 20001", lat: 38.9101, lng: -77.0221 },
    { zip: "20002", label: "Near Northeast 20002", lat: 38.9008, lng: -76.9957 },
    { zip: "20003", label: "Capitol Hill East 20003", lat: 38.8812, lng: -76.9883 },
    { zip: "20004", label: "Southwest / Federal Core 20004", lat: 38.8952, lng: -77.0282 },
    { zip: "20005", label: "Logan Circle 20005", lat: 38.9084, lng: -77.0316 },
    { zip: "20006", label: "West End 20006", lat: 38.8989, lng: -77.0417 },
    { zip: "20007", label: "Georgetown 20007", lat: 38.9136, lng: -77.0715 },
    { zip: "20008", label: "Cleveland Park 20008", lat: 38.9345, lng: -77.0595 },
    { zip: "20009", label: "Adams Morgan 20009", lat: 38.9222, lng: -77.0384 },
    { zip: "20010", label: "Columbia Heights 20010", lat: 38.9318, lng: -77.0293 },
    { zip: "20011", label: "Petworth 20011", lat: 38.9491, lng: -77.0282 },
    { zip: "20012", label: "Takoma 20012", lat: 38.9791, lng: -77.0296 },
    { zip: "20015", label: "Chevy Chase 20015", lat: 38.9641, lng: -77.0594 },
    { zip: "20016", label: "Tenleytown 20016", lat: 38.9388, lng: -77.0887 },
    { zip: "20017", label: "Brookland 20017", lat: 38.9337, lng: -76.9901 },
    { zip: "20018", label: "Woodridge 20018", lat: 38.9277, lng: -76.9716 },
    { zip: "20019", label: "Deanwood 20019", lat: 38.8896, lng: -76.9531 },
    { zip: "20020", label: "Anacostia 20020", lat: 38.8623, lng: -76.9774 },
    { zip: "20024", label: "Southwest Waterfront 20024", lat: 38.8767, lng: -77.0171 },
    { zip: "20032", label: "Congress Heights 20032", lat: 38.8399, lng: -76.9964 },
    { zip: "20036", label: "Dupont / Downtown Residential 20036", lat: 38.9075, lng: -77.0418 },
    { zip: "20037", label: "West End North 20037", lat: 38.899, lng: -77.0501 }
  ];

  const neighborhoodAreas = [
    { label: "Petworth", lat: 38.9418, lng: -77.0242, aliases: ["petworth", "brightwood", "16th street heights"] },
    { label: "Columbia Heights", lat: 38.9287, lng: -77.0322, aliases: ["columbia heights", "park view"] },
    { label: "Shaw", lat: 38.9143, lng: -77.0219, aliases: ["shaw", "logan circle", "downtown dc", "downtown", "mount vernon triangle"] },
    { label: "Georgetown", lat: 38.9136, lng: -77.0715, aliases: ["georgetown", "glover park", "palisades", "burleith"] },
    { label: "Tenleytown", lat: 38.946, lng: -77.0775, aliases: ["tenleytown", "tenley", "chevy chase", "friendship heights"] },
    { label: "Brookland", lat: 38.9325, lng: -76.9958, aliases: ["brookland", "edgewood", "michigan park"] },
    { label: "Capitol Hill East", lat: 38.8896, lng: -76.9894, aliases: ["capitol hill", "capitol hill east", "hill east", "h street", "union station"] },
    { label: "Southwest Waterfront", lat: 38.8768, lng: -77.0243, aliases: ["southwest", "wharf", "waterfront"] },
    { label: "Deanwood", lat: 38.8894, lng: -76.9488, aliases: ["deanwood", "benning", "marshall heights"] },
    { label: "Anacostia", lat: 38.8625, lng: -76.9802, aliases: ["anacostia", "skyland", "fairlawn"] },
    { label: "Congress Heights", lat: 38.8445, lng: -76.9925, aliases: ["congress heights", "washington highlands", "bellevue"] }
  ];

  const campusLocations = [
    { label: "Howard University", lat: 38.9227, lng: -77.0194, aliases: ["howard", "howard university", "20059", "20060"] },
    { label: "Georgetown University", lat: 38.9081, lng: -77.0722, aliases: ["georgetown university", "gu", "20057"] },
    { label: "George Washington University", lat: 38.8997, lng: -77.047, aliases: ["gw", "gwu", "george washington university", "20052"] },
    { label: "American University", lat: 38.9371, lng: -77.0891, aliases: ["american university", "au"] },
    { label: "Catholic University", lat: 38.9369, lng: -76.9989, aliases: ["catholic university", "20064"] },
    { label: "UDC", lat: 38.9441, lng: -77.0656, aliases: ["udc", "university of the district of columbia"] }
  ];

  const knownLocations = {};

  residentZipAreas.forEach(function (entry) {
    knownLocations[entry.zip] = {
      label: entry.label,
      lat: entry.lat,
      lng: entry.lng
    };
  });

  neighborhoodAreas.forEach(function (entry) {
    entry.aliases.forEach(function (alias) {
      knownLocations[alias] = {
        label: entry.label,
        lat: entry.lat,
        lng: entry.lng
      };
    });
  });

  campusLocations.forEach(function (entry) {
    entry.aliases.forEach(function (alias) {
      knownLocations[alias] = {
        label: entry.label,
        lat: entry.lat,
        lng: entry.lng
      };
    });
  });

  const categoryMeta = {
    snacks: { id: "snacks", name: "Healthy snacks", short: "Snacks" },
    veg: { id: "veg", name: "Produce and veg", short: "Fresh" },
    nonveg: { id: "nonveg", name: "Protein and meals", short: "Protein" },
    bread: { id: "bread", name: "Bread and wraps", short: "Bread" },
    pantry: { id: "pantry", name: "Pantry staples", short: "Pantry" },
    boxes: { id: "boxes", name: "Support boxes", short: "Boxes" }
  };

  const catalogCategories = [
    { id: "all", name: "All groceries" },
    { id: "snacks", name: "Healthy snacks" },
    { id: "veg", name: "Produce and veg" },
    { id: "nonveg", name: "Protein and meals" },
    { id: "bread", name: "Bread and wraps" },
    { id: "pantry", name: "Pantry staples" }
  ];

  const products = [
    { id: "apple_pb", name: "Apple and peanut butter pack", cat: "snacks", diet: "veg", price: 1.49, retail: 2.29, unit: "1 apple + 1.5 oz peanut butter", portion: "1 snack", kcal: 260, protein: 8, fiber: 6, tag: "Fresh snack", budget: true, baseStock: 38 },
    { id: "yogurt_parfait", name: "Greek yogurt parfait", cat: "snacks", diet: "veg", price: 1.79, retail: 2.99, unit: "7 oz cup", portion: "1 cup", kcal: 190, protein: 15, fiber: 3, tag: "High protein", budget: true, baseStock: 34 },
    { id: "hummus_carrots", name: "Hummus and carrot cup", cat: "snacks", diet: "veg", price: 1.69, retail: 2.79, unit: "6 oz cup", portion: "1 snack", kcal: 210, protein: 7, fiber: 7, tag: "Veg snack", budget: true, baseStock: 32 },
    { id: "trail_mix", name: "Trail mix mini", cat: "snacks", diet: "veg", price: 1.99, retail: 3.49, unit: "3 oz pouch", portion: "1 pouch", kcal: 360, protein: 10, fiber: 4, tag: "Shelf stable", budget: true, baseStock: 42 },
    { id: "popcorn", name: "Low-salt popcorn", cat: "snacks", diet: "veg", price: 1.25, retail: 2.19, unit: "2.5 oz bag", portion: "1 bag", kcal: 150, protein: 4, fiber: 5, tag: "Whole grain", budget: true, baseStock: 45 },
    { id: "banana_oat", name: "Banana oat bites", cat: "snacks", diet: "veg", price: 1.39, retail: 2.29, unit: "2 bites", portion: "1 snack", kcal: 220, protein: 6, fiber: 4, tag: "Quick breakfast", budget: true, baseStock: 30 },
    { id: "salad_kit", name: "Fresh salad kit", cat: "veg", diet: "veg", price: 2.99, retail: 4.99, unit: "11 oz kit", portion: "2 portions", kcal: 240, protein: 8, fiber: 8, tag: "Fresh", budget: true, baseStock: 22 },
    { id: "lentil_bowl", name: "Lentil protein bowl", cat: "veg", diet: "veg", price: 3.49, retail: 5.49, unit: "14 oz bowl", portion: "1 meal", kcal: 420, protein: 20, fiber: 13, tag: "High protein", budget: true, baseStock: 24 },
    { id: "tofu_kit", name: "Tofu stir-fry kit", cat: "veg", diet: "veg", price: 4.49, retail: 6.99, unit: "18 oz kit", portion: "2 meals", kcal: 520, protein: 26, fiber: 10, tag: "Dinner", budget: false, baseStock: 18 },
    { id: "frozen_veg", name: "Frozen veg mix", cat: "veg", diet: "veg", price: 1.99, retail: 3.29, unit: "12 oz bag", portion: "3 sides", kcal: 180, protein: 6, fiber: 9, tag: "Freezer", budget: true, baseStock: 36 },
    { id: "fruit_cup", name: "Fresh fruit cup", cat: "veg", diet: "veg", price: 1.99, retail: 3.49, unit: "8 oz cup", portion: "1 snack", kcal: 120, protein: 2, fiber: 4, tag: "Fresh", budget: true, baseStock: 28 },
    { id: "egg_box", name: "Egg protein box", cat: "nonveg", diet: "nonveg", price: 2.99, retail: 4.79, unit: "2 eggs + fruit", portion: "1 meal or snack", kcal: 310, protein: 18, fiber: 4, tag: "Protein", budget: true, baseStock: 27 },
    { id: "chicken_rice", name: "Chicken rice bowl", cat: "nonveg", diet: "nonveg", price: 4.99, retail: 7.99, unit: "16 oz bowl", portion: "1 meal", kcal: 560, protein: 36, fiber: 5, tag: "Hot meal base", budget: false, baseStock: 20 },
    { id: "tuna_pack", name: "Tuna protein pack", cat: "nonveg", diet: "nonveg", price: 3.49, retail: 5.79, unit: "Tuna + crackers", portion: "1 meal or snack", kcal: 340, protein: 24, fiber: 3, tag: "Shelf stable", budget: true, baseStock: 31 },
    { id: "turkey_wrap", name: "Turkey veg wrap", cat: "nonveg", diet: "nonveg", price: 3.99, retail: 6.49, unit: "1 wrap", portion: "1 meal", kcal: 430, protein: 25, fiber: 5, tag: "Grab and go", budget: true, baseStock: 23 },
    { id: "chicken_pack", name: "Chicken family pack", cat: "nonveg", diet: "nonveg", price: 8.99, retail: 12.99, unit: "1.5 lb pack", portion: "4 portions", kcal: 980, protein: 132, fiber: 0, tag: "Bulk value", budget: false, baseStock: 12 },
    { id: "wheat_bread", name: "Whole wheat bread", cat: "bread", diet: "veg", price: 2.29, retail: 3.49, unit: "20 oz loaf", portion: "20 slices", kcal: 70, protein: 4, fiber: 2, tag: "Bread", budget: true, baseStock: 35 },
    { id: "wraps", name: "Whole grain wraps", cat: "bread", diet: "veg", price: 1.99, retail: 3.29, unit: "6 count pack", portion: "6 wraps", kcal: 140, protein: 5, fiber: 4, tag: "Meal prep", budget: true, baseStock: 29 },
    { id: "bagels", name: "Mini bagel pack", cat: "bread", diet: "veg", price: 2.49, retail: 4.29, unit: "6 mini bagels", portion: "6 portions", kcal: 130, protein: 5, fiber: 2, tag: "Breakfast", budget: true, baseStock: 26 },
    { id: "pita", name: "Pita bread pack", cat: "bread", diet: "veg", price: 1.79, retail: 2.99, unit: "5 count pack", portion: "5 pitas", kcal: 160, protein: 6, fiber: 3, tag: "Low cost", budget: true, baseStock: 24 },
    { id: "rice", name: "Brown rice", cat: "pantry", diet: "veg", price: 3.99, retail: 6.29, unit: "5 lb bag", portion: "25 servings", kcal: 170, protein: 4, fiber: 2, tag: "Staple", budget: true, baseStock: 44 },
    { id: "beans", name: "Black beans", cat: "pantry", diet: "veg", price: 1.29, retail: 1.99, unit: "15 oz can", portion: "3.5 servings", kcal: 110, protein: 7, fiber: 6, tag: "Protein", budget: true, baseStock: 62 },
    { id: "oats", name: "Rolled oats", cat: "pantry", diet: "veg", price: 2.79, retail: 4.49, unit: "42 oz tub", portion: "30 servings", kcal: 150, protein: 5, fiber: 4, tag: "Breakfast", budget: true, baseStock: 39 },
    { id: "pasta", name: "Whole wheat pasta", cat: "pantry", diet: "veg", price: 1.39, retail: 2.29, unit: "16 oz box", portion: "8 servings", kcal: 180, protein: 7, fiber: 5, tag: "Dinner", budget: true, baseStock: 41 },
    { id: "milk", name: "Low-fat milk", cat: "pantry", diet: "veg", price: 2.99, retail: 4.39, unit: "Half gallon", portion: "8 cups", kcal: 120, protein: 8, fiber: 0, tag: "Chilled", budget: false, baseStock: 25 }
  ];

  const boxes = [
    { id: "solo_box", name: "Solo essentials box", cat: "boxes", diet: "mixed", price: 12.49, retail: 19.9, unit: "Weekly mixed grocery box", portion: "7 meal or snack portions", kcal: 2650, protein: 62, fiber: 28, tag: "Resident box", budget: true, baseStock: 18, contents: "Oats, fruit, beans, bread, greens, and one protein item" },
    { id: "produce_box", name: "Produce support box", cat: "boxes", diet: "veg", price: 13.49, retail: 22.4, unit: "Produce-focused box", portion: "8 portions", kcal: 1980, protein: 40, fiber: 38, tag: "Produce box", budget: true, baseStock: 16, contents: "Greens, fruit, carrots, frozen vegetables, beans, and wraps" },
    { id: "protein_box", name: "Protein support box", cat: "boxes", diet: "mixed", price: 15.99, retail: 25.8, unit: "Protein-focused box", portion: "8 portions", kcal: 3120, protein: 116, fiber: 22, tag: "Protein box", budget: true, baseStock: 15, contents: "Eggs, beans, chicken or tuna, wraps, and fruit" },
    { id: "family_box", name: "Family pantry box", cat: "boxes", diet: "mixed", price: 24.99, retail: 41.5, unit: "Family grocery box", portion: "14 portions", kcal: 5520, protein: 148, fiber: 54, tag: "Family support", budget: true, baseStock: 12, contents: "Rice, beans, bread, eggs or chicken, vegetables, fruit, and milk" }
  ];

  root.data = {
    mapRadiusMiles: 1,
    mapRadiusMeters: 1609.34,
    defaultOrigin: null,
    residentZipAreas: residentZipAreas,
    pitStops: pitStops,
    knownLocations: knownLocations,
    categoryMeta: categoryMeta,
    catalogCategories: catalogCategories,
    products: products,
    boxes: boxes,
    allItems: products.concat(boxes)
  };
})();
