
if (typeof(openerp) == "undefined") {
    openerp = new Object;
}

if (typeof(openerp.workflow) == "undefined") {
    openerp.workflow = new Object;
}

openerp.workflow.ConnectionAnchor = new Class;
openerp.workflow.ConnectionAnchor.prototype = $merge(openerp.workflow.ConnectionAnchor.prototype, draw2d.ChopboxConnectionAnchor.prototype);

openerp.workflow.ConnectionAnchor.implement({

	initialize : function(owner) {
		draw2d.ChopboxConnectionAnchor.call(this,owner);
		this.conn_id = 0;
		this.factor = 6;
		
	},
	

getLocation : function(/*:draw2d.Point*/ reference)
	{		
		
		var center = this.getReferencePoint();
		var bounds = this.getBox();
		var b2 = (bounds.h/2) * (bounds.h/2);//minor axis of ellipse
		var a2 = (bounds.w/2) * (bounds.w/2);//major axis of ellipse
		
		var ry = reference.y - center.y
		var rx = reference.x - center.x
		if(rx!=0)
			var slope = ry / rx;
		
		var connectors = this.owner.getConnections();
		var n = connectors.getSize();
		
		for(i=0; i<n; i++)
			if(connectors.get(i).tr_id==this.conn_id) {
				var conn = connectors.get(i);
				break;
			}	
		//multiple connectors		
		if(conn.isOverlaping) {	
			
			//vertical parallel lines
			if(rx==0) {
				var x = bounds.w / 2;
				var y = 0;		
			}//horizontal parallel lines			
			else if(ry==0) {
				var x = 0;
				var y = bounds.h / 2;
			} 
			else {
				
				var m = -1/slope; //slope of perpendicular line  is negative of resiprocal of slope				
				
				//solving equation of ellipse and line which is prependicular to the line passing through two center 
				var x = Math.sqrt((a2 * b2) / (b2 + (m * m * a2)));
				var y = m * x;		
			}
			
			var xd = -2 * x;
			var yd = -2 * y;	
			var k = 1/(conn.totalOverlaped + 1);
			
			var xnew = x + (k * xd * conn.OverlapingSeq); 
			var ynew = y + (k * yd * conn.OverlapingSeq);
		}
		else {//single connector
			var xnew = 0;
			var ynew = 0;			
		}
		
		//find point on ellipse
		if(rx!=0) {
			
			var c = ynew - (slope * xnew);
					
			var A = (b2) + ((a2) * (slope*slope));
			var B = 2 * c * slope * (a2);
			var C = (a2) * ((c*c) - (b2));
			
			var discriminator = Math.sqrt((B*B) - (4 * A *C));
			
			var root1x = (-B + discriminator)/(2 * A);
			var root2x = (-B - discriminator)/(2 * A);
			
			//substituting x in y=mx+c
			var root1y = slope*root1x + c;
			var root2y = slope*root2x + c;
		}
		else {			
			var root1x = xnew;
			var root2x = xnew;
			
			var root1y = Math.sqrt((b2 * (a2 - (root1x*root1x)))/(a2))
			var root2y = -root1y;
		}
		
		var dist1 = Math.sqrt(((rx-root1x)*(rx-root1x)) + ((ry-root1y)*(ry-root1y)));
		var dist2 = Math.sqrt(((rx-root2x)*(rx-root2x)) + ((ry-root2y)*(ry-root2y)));

		if(dist2>dist1)
			return new draw2d.Point(Math.round(center.x + root1x), Math.round(center.y + root1y));
		else
			return new draw2d.Point(Math.round(center.x + root2x), Math.round(center.y + root2y));
	},
});