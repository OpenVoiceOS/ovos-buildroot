var dashboard_model = []
var flow_model = []
var dashboard_spacing
var dashboard_available_width
var dashboard_available_height

var available_width = {
    width: 0,
    getActualWidth() {
      return this.width;
    },
    setActualWidth(value) {
      this.width = value;
      dashboard_available_width = value
      widthOnChanged();
    }
};

var available_height = {
    height: 0,
    getActualHeight() {
      return this.height;
    },
    setActualHeight(value) {
      this.height = value;
      dashboard_available_height = value;
      heightOnChanged();
    }
};

function add_items_from_session(collection) {
    if (collection.length == 0) {
        return;
    }

    for (var i = 0; i < collection.length; i++) {
        var item = collection[i];
        if (!item_in_flow_model(item)) {
            add_item(item);
        } else {
            console.log("Item already in flow model");
        }
    }
}

function item_in_flow_model(item) {
    for (var i = 0; i < flow_model.length; i++) {
        if (flow_model[i].id == item.id) {
            return true;
        }
    }
    return false;
}

function widthOnChanged() {
    for (var i = 0; i < flow_model.length; i++) {
        flow_model[i].width = get_width(flow_model[i].cellWidth);
    }
    update_dashboard_model()
}

function heightOnChanged() {
    for (var i = 0; i < flow_model.length; i++) {
        flow_model[i].height = get_height(flow_model[i].cellHeight);
    }
    update_dashboard_model()
}

function add_item(item) {
    // Add the calculated height and width to the item
    item.height = get_height(item.cellHeight);
    item.width = get_width(item.cellWidth);
    if (!item_in_flow_model(item)) {
        flow_model.push(item);
    } else {
        console.log("Item already in flow model");
    }

    update_dashboard_model()
}

function get_item(index) {
    return flow_model[index];
}

function get_item_count() {
    return flow_model.length;
}

function clear_model() {
    flow_model = [];
    update_dashboard_model();
}

function remove_item(index) {
    flow_model.splice(index, 1);
    update_dashboard_model();
}

function remove_item_by_id(cardID) {
    for (var i = 0; i < flow_model.length; i++) {
        if (flow_model[i].id == cardID) {
            flow_model.splice(i, 1);
            update_dashboard_model();
            return;
        }
    }
}

function update_dashboard_model() {
    dashboard_model = []
    for (var i = 0; i < flow_model.length; i++) {
        dashboard_model.push(flow_model[i]);
    }
    repeaterModel.model = []
    repeaterModel.model = dashboard_model
}

function get_height(requiredCellHeight) {
    if (requiredCellHeight == 1) {
        return dashboard_available_height * 0.1 - dashboard_spacing;
    } else if (requiredCellHeight == 2) {
        return dashboard_available_height * 0.2 - dashboard_spacing;
    }
    else if (requiredCellHeight == 3) {
        return dashboard_available_height * 0.3 - dashboard_spacing;
    }
    else if (requiredCellHeight == 4) {
        return dashboard_available_height * 0.4 - dashboard_spacing;
    }
    else if (requiredCellHeight == 5) {
        return dashboard_available_height * 0.5 - dashboard_spacing;
    }
    else if (requiredCellHeight == 6) {
        return dashboard_available_height * 0.6 - dashboard_spacing;
    }
    else if (requiredCellHeight == 7) {
        return dashboard_available_height * 0.7 - dashboard_spacing;
    }
    else if (requiredCellHeight == 8) {
        return dashboard_available_height * 0.8 - dashboard_spacing;
    }
    else if (requiredCellHeight == 9) {
        return dashboard_available_height * 0.9 - dashboard_spacing;
    }
    else if (requiredCellHeight == 10) {
        return dashboard_available_height - dashboard_spacing;
    } else {
        return dashboard_available_height * 0.5 - dashboard_spacing;
    }
}

function get_width(requiredCellWidth) {
    if (requiredCellWidth <= 5) {
        return Math.round(dashboard_available_width * 0.5 - dashboard_spacing)
    }
    else if (requiredCellWidth > 5) {
        return Math.round(dashboard_available_width - dashboard_spacing)
    }
}
