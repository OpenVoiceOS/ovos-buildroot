function isLight(color) {
    // Convert color to string
    color = color.toString();

    var color_r = color.slice(1,3);
    var color_g = color.slice(3,5);
    var color_b = color.slice(5,7);

    var r = parseInt(color_r, 16);
    var g = parseInt(color_g, 16);
    var b = parseInt(color_b, 16);

    var hsp = Math.sqrt(
      0.299 * (r * r) +
      0.587 * (g * g) +
      0.114 * (b * b)
    );

    if (hsp>127.5) {

      return true;
    }
    else {

      return false;
    }
}
