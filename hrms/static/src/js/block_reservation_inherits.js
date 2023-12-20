openerp.hrms = function (instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    openerp.hotel_reservation.RoomSummary.include({
        initialize_content: function(message) {
            var self = this;
            this._super.apply(this, arguments);
            this.view_loading_block();
            // this.view_loading_reser();
    
        },

        view_loading_block: function(m) {
            return this.load_form_block(m);
        },

        // view_loading_reser: function(n) {
        //     return this.load_form_reser(n);
        // },
        
        load_form_block: function(data) {
            self.action_manager = new openerp.web.ActionManager(self);
            
            this.$el.find(".table_block").bind("click", function(event){
                self.action_manager.do_action({
                        type: 'ir.actions.act_window',
                        res_model: "quick.room.reservation.view",
                        views: [[false, 'form']],
                        target: 'new',
                        context: {"room_id": $(this).attr("data"), 'date': $(this).attr("date")},
                });
            });

            // this.$el.find(".table_reserved").bind("click", function(events){
            //     self.action_manager.do_action({
            //             type: 'ir.actions.act_window',
            //             res_model: "quick.room.reservation.table",
            //             views: [[false, 'form']],
            //             target: 'new',
            //             context: {"room_id": $(this).attr("data"), 'date': $(this).attr("date")},
            //     });
            // });

        },

        // load_form_reser: function(data) {
        //     self.action_manager = new openerp.web.ActionManager(self);
            
        //     this.$el.find(".table_reserved").bind("click", function(event){
        //         self.action_manager.do_action({
        //                 type: 'ir.actions.act_window',
        //                 res_model: "quick.room.reservation.table",
        //                 views: [[false, 'form']],
        //                 target: 'new',
        //                 context: {"room_id": $(this).attr("data"), 'date': '2018-01-10 00:00:00'},
        //         });
        //     });

        // },
    });
}
