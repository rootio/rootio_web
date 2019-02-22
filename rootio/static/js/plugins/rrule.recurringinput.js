/*
 * A JQuery UI Widget to create a RRule compatible inputs for use inside a form
 * Requires: rrule.js (http://jkbr.github.io/rrule/)
 *          underscore.js
 * Author: Josh Levinger, 2013
 */

// add helpful constants to RRule
RRule.FREQUENCY_NAMES = [/*'year','month',*/'week','day','hour','minute','second'];
RRule.DAYCODES = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
RRule.DAYNAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
RRule.MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
// note, month num for these values should be one-based, not zero-based

$.widget("rrule.recurringinput", {
  // default options
  options: {
    freq: RRule.WEEKLY,
    count: 1
  },

  _create: function() {
    //set up inputs
    // TODO: convert to underscore template
    var tmpl = "<!-- janky inline template -->";

    //frequency
    tmpl += '<div class="input-prepend">';
    tmpl += '<span class="add-on">Repeat</span>';
    tmpl += '<select name="freq" class="span2">';
    _.each(RRule.FREQUENCIES, function(element, index) {
      if (['yearly', 'monthly'].includes(element.toLowerCase())) {
        return; // remove yearly and monthly frequencies for now
      }
      var f = window['RRule'][element]; //use window[] syntax to get object from string
      tmpl += '<option value='+f+'>'+element.toLowerCase()+'</option>';
    });
    tmpl += '</select>';
    tmpl += '</div>';

    tmpl += '<br>';

    tmpl += '<div class="input-prepend input-append">';
    tmpl += '<span class="add-on">Every</span>';
    tmpl += '<input type="number" class="span2" value="1" min="1" max="100" name="interval"/>';
    tmpl += '<span class="add-on" id="frequency_name"></span>';
    tmpl += '</div>';


    // repeat options, frequency specific
    // data-freq should be lowercase value from FREQUENCY_NAMES

    // bymonth (works, temporarily disabled)
    //
    // tmpl += '<div class="repeat-options controls form-inline" data-freq="monthly"><label>Only in ';
    // _.each(RRule.MONTHS, function(element, index) {
    //   tmpl += '<label class="inline">';
    //   tmpl += '<input type="checkbox" name="bymonth" value="'+(index+1)+'" />';
    //   tmpl += element+'</label>';
    // });
    // tmpl += '</div>';

    // by weekday
    //
    tmpl += '<div class="repeat-options controls form-inline" data-freq="weekly">';

    tmpl += '<div class="weekdays-selector">';

    _.each(RRule.DAYCODES, function(element, index) {
      var d = window['RRule'][element];

      tmpl += '<input type="checkbox" name="byweekday" id="weekday-'+d.weekday+'" class="weekday" value="'+d.weekday+'" />';
      tmpl += '<label for="weekday-'+d.weekday+'">'+RRule.DAYNAMES[index].slice(0,3)+'</label>';
    });
    tmpl += '</div>';
    tmpl += '</div>';

    // by hour
    //
    tmpl += '<br>';
    tmpl += '<div class="input-prepend input-append repeat-options" data-freq="hourly">';
    tmpl += '<span class="add-on">Only at</span>';
    tmpl += '<input type="number" class="span2" name="byhour" value="0" min="0" max="23" />';
    tmpl += '<span class="add-on">o\'clock</span>';
    tmpl += '</div>';

    // by minute
    //
    tmpl += '<div class="input-prepend input-append repeat-options" data-freq="minutely">';
    tmpl += '<span class="add-on">Only at</span>';
    tmpl += '<input type="number" class="span2" name="byminute" value="0" min="0" max="59" />';
    tmpl += '<span class="add-on">minutes</span>';
    tmpl += '</div>';

    // by second
    //
    tmpl += '<div class="input-prepend input-append repeat-options" data-freq="secondly">';
    tmpl += '<span class="add-on">Only at</span>';
    tmpl += '<input type="number" class="span2" name="bysecond" value="0" min="0" max="59" />';
    tmpl += '<span class="add-on">seconds</span>';
    tmpl += '</div>';

    // end repeat options

    // starts on
    tmpl += '<br>';
    tmpl += '<div class="input-prepend">';
    tmpl += '<span class="add-on">Start</span>';
    tmpl += '<input class="span2" name="dtstart" type="date" />';
    tmpl += '</div>';

    // end on

    tmpl += '<br>';
    tmpl += '<div class="input-prepend input-append">';
    tmpl += '<span class="add-on">End</span>';
    tmpl += '<input type="radio" checked hidden name="end" value="2">';
    tmpl += '<input class="span2" name="until" type="date" />';
    tmpl += '<span class="add-on">(optional)</span>';
    tmpl += '</div>';
    tmpl += '<br>';
    tmpl += '<small><em>No end date will make the program run for an year</em></small>';

    // // Stop after a number of occurrences (works, temporarily disabled)
    // //
    // // tmpl += '<label class="inline">';
    // // tmpl += '<input type="radio" name="end" value="1" /> After <input type="number" max="1000" min="1" value="" name="count"/> occurences';
    // // tmpl += '</label>';

    // summary
    tmpl += '<div class="hidden">';
    tmpl += '<label for="output">Summary ';
    tmpl += '<em id="text-output"></em></label>'; // human readable
    tmpl += '<br><label>RRule <code id="rrule-output"></code></label>'; // ugly rrule
    tmpl += '</div>';
    //TODO: show next few instances to help user debug

    //render template
    this.element.append(tmpl);

    //save input references to widget for later use
    this.frequency_select = this.element.find('select[name="freq"]');
    this.interval_input = this.element.find('input[name="interval"]');
    this.start_input = this.element.find('input[name="dtstart"]');
    this.end_input = this.element.find('input[type="radio"][name="end"]');

    //bind event handlers
    this._on(this.element.find('select, input'), {
      'change': this._refresh
    });

    //set sensible defaults
    this.frequency_select.val(2);
    this.interval_input.val(1);
    this.start_input.val(moment().format('YYYY-MM-DD'));

    //refresh
    this._refresh();
 },

  // called on create and when changing options
  _refresh: function() {
    //determine selected frequency
    var frequency = this.frequency_select.find("option:selected");
    // fill in frequency-name span
    this.element.find('#frequency_name').text(RRule.FREQUENCY_NAMES[frequency.val()]);
    // and pluralize
    if (this.interval_input.val() > 1) {
      this.element.find('#frequency_name').append('s');
    }

    // display appropriate repeat options
    var repeatOptions = this.element.find('.repeat-options');
    repeatOptions.hide();

    if (frequency !== "") {
      //show options for the selected frequency
      var selectedOptions = repeatOptions.filter('[data-freq='+frequency.text()+']');
      selectedOptions.show();

      //and clear descendent fields for the others
      nonSelectedOptions = repeatOptions.filter('[data-freq!='+frequency.text()+']');
      nonSelectedOptions.find('input[type=checkbox]:checked').removeAttr('checked');
      nonSelectedOptions.find('select').val('');
    }

    // //reset end
    // switch (this.end_input.filter(':checked').val()) {
    //   case "0":
    //     //never, clear count and until
    //     this.end_input.siblings('input[name=count]').val('');
    //     this.end_input.siblings('input[name=until]').val('');
    //     break;
    //   case "1":
    //     //after, clear until
    //     this.end_input.siblings('input[name=until]').val('');
    //     break;
    //   case "2":
    //     //date, clear count
    //     this.end_input.siblings('input[name=count]').val('');
    //     break;
    // }

    //determine rrule
    var rrule = this._getRRule();

    $('#rrule-output').text(rrule.toString());
    $('#text-output').text(rrule.toText());
    this.element.trigger('rrule-update');
  },

  _getFormValues: function($form) {
    //modified from rrule/tests/demo/demo.js
    var paramObj;
    paramObj = {};

    $.each($form.serializeArray(), function(_, kv) {
      if (paramObj.hasOwnProperty(kv.name)) {
        paramObj[kv.name] = $.makeArray(paramObj[kv.name]);
        return paramObj[kv.name].push(kv.value);
      } else {
        return paramObj[kv.name] = kv.value;
      }
    });
    return paramObj;
  },
  _getRRule: function() {
    //modified from rrule/tests/demo/demo.js
    //ignore 'end', because it's part of the ui but not the spec
    values = this._getFormValues($(this.element).find('select, input[name!=end]'));

    options = {};
    getDay = function(i) {
      return [RRule.MO, RRule.TU, RRule.WE, RRule.TH, RRule.FR, RRule.SA, RRule.SU][i];
    };
    for (k in values) {
      v = values[k];
      if (!v) {
        continue;
      }
      if (_.contains(["dtstart", "until"], k)) {
        d = new Date(Date.parse(v));
        v = new Date(d.getTime());
      } else if (k === 'byweekday') {
        if (v instanceof Array) {
          v = _.map(v, getDay);
        } else {
          v = getDay(v);
        }
      } else if (/^by/.test(k)) {
        if (!(v instanceof Array)) {
          v = _.compact(v.split(/[,\s]+/));
        }
        v = _.map(v, function(n) {
          return parseInt(n, 10);
        });
      } else {
        v = parseInt(v, 10);
      }
      if (k === 'wkst') {
        v = getDay(v);
      }
      if (k === 'interval' && v === 1) {
        continue;
      }
      options[k] = v;
    }
    try {
        rule = new RRule(options);
      } catch (_error) {
        e = _error;
        $("#text-output").append($('<pre class="error"/>').text('=> ' + String(e || null)));
        return;
      }
    return rule;
  },

  // _setOptions is called with a hash of all options that are changing
  // always refresh when changing options
  _setOptions: function() {
    this._superApply( arguments );
    this._refresh();
  },

  destroy: function() {
    // remove references
    this.frequency_select.remove();
    this.interval_input.remove();

    // unbind events

    // clear templated html
    this.element.html("");

    $.Widget.prototype.destroy.apply(this);
 }
});
