webpackJsonp([4],{"6WW2":function(t,e,a){"use strict";e.b=function(){return o.b?i.a.post("/api/getmoviepiaofang"):new r.a(function(t,e){setTimeout(t,2e3,i.a.post("/api/getmoviepiaofang-mock"))})},e.a=function(){return i()({method:"post",url:"/excel/getMergeTableData"})};var l=a("//Fk"),r=a.n(l),n=a("mtWM"),i=a.n(n),o=a("0xDb")},D3JS:function(t,e){},TmV0:function(t,e,a){a("fZOM"),t.exports=a("FeBl").Object.values},cK4b:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var l=a("gRE1"),r=a.n(l),n=a("6WW2"),i={data:function(){return{isDev:null,downloadLoading:!1,tableDataLoading:!0,tableData:[],filename:"",autoWidth:!0,refresh:!0,percentageNum:100,timer:0,updateTime:""}},methods:{_getTable:function(){var t=this;Object(n.b)().then(function(e){if(t.isDev){var a=e.data.real.data.detail;t.updateTime=e.data.real.data.total.message,t.formatMovieData(a),t.tableData=a,t.tableDataLoading=!1}else{e.data=JSON.parse(e.data);var l=e.data.real.data.detail;t.updateTime=e.data.real.data.total.message,t.formatMovieData(l),t.tableData=l,t.tableDataLoading=!1}})},updateData:function(){var t=this;this.refresh=!1,this.percentageNum=0,this.timer=window.setInterval(function(){t.percentageNum<100?t.percentageNum+=1:(t.percentageNum=100,t.refresh=!0,window.clearInterval(t.timer))},100),this.tableDataLoading=!0,this._getTable()},handleDownload:function(){var t=this;this.downloadLoading=!0,a.e(14).then(a.bind(null,"zWO4")).then(function(e){var a=t.tableData,l=t.formatJson(["影片","上映天数","累计票房","实时票房","票房占比","排片占比","上座率","排座占比","场次","人次","场均人次","场均收入","平均票价"],a);e.export_json_to_excel({header:["影片","上映天数","累计票房","实时票房","票房占比","排片占比","上座率","排座占比","场次","人次","场均人次","场均收入","平均票价"],data:l,filename:t.filename||"excel-list",autoWidth:t.autoWidth}),t.downloadLoading=!1})},formatJson:function(t,e){return e.map(function(e){return t.map(function(t){return"影片"===t?e.movieName:e[t]})})},formatMovieData:function(t){t.forEach(function(t){r()(t.attribute).forEach(function(e,a,l){t[e.attrName]=e.attrValue})})}},created:function(){this.isDev=!1,this.tableDataLoading=!0,this._getTable()}},o={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{},[a("el-input",{staticStyle:{width:"350px"},attrs:{autosize:"","prefix-icon":"el-icon-document",placeholder:"请输入文件名（默认excel-list）"},model:{value:t.filename,callback:function(e){t.filename=e},expression:"filename"}}),t._v(" "),a("el-button",{staticStyle:{margin:"0 0 20px 20px"},attrs:{type:"primary",icon:"document",loading:t.downloadLoading},on:{click:t.handleDownload}},[t._v("export excel")]),t._v(" "),a("div",{staticClass:"fresh"},[a("el-progress",{staticClass:"progress",attrs:{"text-inside":!0,"stroke-width":18,percentage:t.percentageNum,status:"success"}}),t._v(" "),a("span",[t._v(t._s(t.updateTime))]),t._v(" "),a("el-button",{directives:[{name:"show",rawName:"v-show",value:t.refresh,expression:"refresh"}],staticClass:"timer",attrs:{icon:"el-icon-refresh",type:"text"},on:{click:t.updateData}},[t._v("更新数据")]),t._v(" "),a("el-button",{directives:[{name:"show",rawName:"v-show",value:!t.refresh,expression:"!refresh"}],staticClass:"timer",attrs:{icon:"el-icon-refresh",type:"text",disabled:""}},[t._v("更新数据")])],1),t._v(" "),a("el-table",{directives:[{name:"loading",rawName:"v-loading",value:t.tableDataLoading,expression:"tableDataLoading"}],staticStyle:{width:"100%"},attrs:{data:t.tableData,height:"700"}},[a("el-table-column",{attrs:{fixed:"",prop:"movieName",label:"影片",width:"200"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[1].attrValue",label:"上映天数",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[2].attrValue",label:"累计票房",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[3].attrValue",label:"实时票房",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[4].attrValue",label:"票房占比",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[5].attrValue",label:"排片占比",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[6].attrValue",label:"上座率",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[7].attrValue",label:"排座占比",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[8].attrValue",label:"场次",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[9].attrValue",label:"人次",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[10].attrValue",label:"场均人次",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[11].attrValue",label:"场均收入",width:"120"}}),t._v(" "),a("el-table-column",{attrs:{prop:"attribute[12].attrValue",label:"平均票价",width:"120"}})],1)],1)},staticRenderFns:[]};var s=a("VU/8")(i,o,!1,function(t){a("D3JS")},"data-v-23f20354",null);e.default=s.exports},fZOM:function(t,e,a){var l=a("kM2E"),r=a("mbce")(!1);l(l.S,"Object",{values:function(t){return r(t)}})},gRE1:function(t,e,a){t.exports={default:a("TmV0"),__esModule:!0}},mbce:function(t,e,a){var l=a("+E39"),r=a("lktj"),n=a("TcQ7"),i=a("NpIQ").f;t.exports=function(t){return function(e){for(var a,o=n(e),s=r(o),u=s.length,c=0,d=[];u>c;)a=s[c++],l&&!i.call(o,a)||d.push(t?[a,o[a]]:o[a]);return d}}}});