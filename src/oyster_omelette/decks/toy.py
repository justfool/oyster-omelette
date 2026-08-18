"""玩具卡，測試樁。正式牌庫接上後再退役。"""

from oyster_omelette.cards import minor, occupation

TOY_CARDS = (
    occupation("wood_collector", "樵夫", "wood", 2),
    occupation("clay_worker", "黏土工", "clay", 2),
    occupation("reed_collector", "蘆葦採集", "reed", 1),
    occupation("day_labor_plus", "零工", "food", 2),
    occupation("stone_picker", "撿石人", "stone", 1),
    occupation("grain_sower", "播種人", "grain", 1),
    occupation("veg_grower", "菜農", "vegetable", 1),
    occupation("forester", "林務員"),
    occupation("clay_digger", "挖黏人"),
    occupation("baker", "麵包師"),
    minor("wood_cart", "運木車", "wood", 2),
    minor("clay_pit_shovel", "挖黏鏟", "clay", 1),
    minor("fishing_rod", "釣竿", "food", 2),
    minor("grain_sack", "穀袋", "grain", 1),
    minor("veg_basket", "菜籃", "vegetable", 1),
    minor("stone_sled", "運石橇", "stone", 1),
    minor("reed_bundle", "蘆葦捆", "reed", 1),
    minor("traveling_ale", "旅行麥酒", "food", 1, traveling=True),
    minor("hearty_stew", "大鍋菜", "food", 3, cost=(("grain", 1),)),
)
