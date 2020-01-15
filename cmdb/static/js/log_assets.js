var workflow;
var $select2assets_event;
var $select2AssetsType;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);

var assets_event;
var assets_type;

var table;

// datatables保存的数据，用json格式
var dataTable = new Array();

var id = 1;

// 入库固定资产所需的数据
var storage_assets_modal = `
        <div class="form-group">
          <label class="col-sm-3 control-label">选择公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">使用部门</label>
          <div class="col-sm-8">
            <select id="using_department" style="width: 100%">
              <option selected="selected" value="0">选择使用部门</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">选择供应商</label>
          <div class="col-sm-8">
            <select id="supplier" style="width: 100%">
              <option selected="selected" value="0">选择供应商</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">类别</label>
          <div class="col-sm-8">
            <select id="ctype" style="width: 100%">
              <option selected="selected" value="0">电子设备</option>
              <option value="1">其他电子设备</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">是否新购买</label>
          <div class="col-sm-8">
            <select id="purchase" style="width: 100%">
              <option selected="selected" value="0">否</option>
              <option value="1">是</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">使用资产模板</label>
          <div class="col-sm-8">
            <select id="assets_template" style="width: 100%">
              <option selected="selected" value="0">选择资产模板</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">资产名称</label>
          <div class="col-sm-8">
            <select id="name" style="width: 100%">
              <option selected="selected" value="0">选择资产名称</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">仓库区域</label>
          <div class="col-sm-8">
            <select id="warehousing_region" style="width: 100%">
              <option selected="selected" value="0">选择仓库区域</option>
            </select>
          </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">CPU</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="with_cpu" placeholder="格式如：i5-3640">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">主板</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="board">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">固态硬盘</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="with_ssd">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">机械硬盘</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="with_disk">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">内存</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="with_mem">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">显卡</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="with_graphics">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">品牌</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="brand">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">规格</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="specification">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择位置</option>
              </select>
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">数量</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="number" value=1>
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">单价</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="price">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">备注</label>
            <div class="col-sm-8">
              <textarea rows="5" class="form-control" id="remark"></textarea>
            </div>
        </div>
`

// 入库固定资产所需要的table
var storage_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>类别</th>
          <th>所属公司</th>
          <th>新购买</th>
          <th>资产名称</th>
          <th>仓库区域</th>
          <th>CPU</th>
          <th>主板</th>
          <th>固态硬盘</th>
          <th>机械硬盘</th>
          <th>内存</th>
          <th>显卡</th>
          <th>品牌</th>
          <th>规格</th>
          <th>使用部门</th>
          <th>位置</th>
          <th>供应商</th>
          <th>单价</th>
          <th>备注</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 入库主机配件所需要的数据
var storage_sub_assets_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">所属公司</label>
          <div class="col-sm-8">
            <select id="company" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">是否新购买</label>
          <div class="col-sm-8">
            <select id="purchase" style="width: 100%">
              <option selected="selected" value="0">否</option>
              <option value="1">是</option>
            </select>
          </div>
        </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">类型</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='sub_assets_type'>
                <option value="-1" disabled selected>请选择资产类型</option>
                <option value="0">CPU</option>
                <option value="1">主板</option>
                <option value="2">固态硬盘</option>
                <option value="3">机械硬盘</option>
                <option value="4">内存</option>
                <option value="5">显卡</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">品牌</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="brand">
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">型号</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="smodel">
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number">
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">选择供应商</label>
          <div class="col-sm-8">
            <select id="supplier" style="width: 100%">
              <option selected="selected" value="0">选择供应商</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">单价</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="price">
          </div>
      </div>
`

// 入庫主机配件所需要的table
var storage_sub_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>所属公司</th>
          <th>新购买</th>
          <th>类别</th>
          <th>品牌</th>
          <th>型号</th>
          <th>数量</th>
          <th>位置</th>
          <th>供应商</th>
          <th>单价</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 入库列管资产所需的数据
var storage_shell_assets_modal = `
        <div class="form-group">
          <label class="col-sm-3 control-label">选择公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">选择供应商</label>
          <div class="col-sm-8">
            <select id="supplier" style="width: 100%">
              <option selected="selected" value="0">选择供应商</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">类别</label>
          <div class="col-sm-8">
            <select id="ctype" style="width: 100%">
              <option selected="selected" value="0">电子设备</option>
              <option value="1">其他电子设备</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="col-sm-3 control-label">是否新购买</label>
          <div class="col-sm-8">
            <select id="purchase" style="width: 100%">
              <option selected="selected" value="0">否</option>
              <option value="1">是</option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label class="col-sm-3 control-label">资产名称</label>
          <div class="col-sm-8">
            <select id="name" style="width: 100%">
              <option selected="selected" value="0">选择资产名称</option>
            </select>
          </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">品牌</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="brand">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">规格</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="specification">
            </div>
        </div>
        <div class="form-group">
          <label class="col-sm-3 control-label">使用部门</label>
          <div class="col-sm-8">
            <select id="using_department" style="width: 100%">
              <option selected="selected" value="0">选择使用部门</option>
            </select>
          </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择位置</option>
              </select>
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">数量</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="number" value=1>
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">单价</label>
            <div class="col-sm-8">
              <input type="text" class="form-control" id="price">
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-3 control-label">备注</label>
            <div class="col-sm-8">
              <textarea rows="5" class="form-control" id="remark"></textarea>
            </div>
        </div>
`

// 入库列管资产所需的table
var storage_shell_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>所属公司</th>
          <th>类别</th>
          <th>新购买</th>
          <th>资产名称</th>
          <th>品牌</th>
          <th>型号</th>
          <th>使用部门</th>
          <th>位置</th>
          <th>供应商</th>
          <th>单价</th>
          <th>备注</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`


// 领用固定资产所需的数据
var receive_assets_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">选择公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <!--<div class="form-group">-->
          <!--<label class="col-sm-3 control-label">使用部门</label>-->
          <!--<div class="col-sm-8">-->
            <!--<select id="using_department" style="width: 100%">-->
              <!--<option selected="selected" value="0">选择使用部门</option>-->
            <!--</select>-->
          <!--</div>-->
      <!--</div>-->
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
`


// 领用固定资产领用的table

var receive_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <!--<th>公司</th>-->
          <th>资产编号</th>
          <th>位置</th>
          <!--<th>使用部门</th>-->
          <th>保管人</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`


// 领用固定资产合并所需的数据
var receive_assets_merge_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">被合并资产</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='merge_assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">主资产</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
`

// 领用固定资产合并所需的table
var receive_assets_merge_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>主资产</th>
          <th>被合并资产</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 领用主机配件所需的数据
var receive_sub_asssets_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">配件来源公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">配件来源位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择来源位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">配件类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">配件型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">配件并入资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`


// 领用主机配件所需的table
var receive_sub_asssets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>公司</th>
          <th>型号</th>
          <th>类型</th>
          <th>来源位置</th>
          <th>资产编号</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`


// 调换固定资产所需的数据
var exchange_assets_modal = `
      <!--<div class="form-group">
          <label class="col-sm-3 control-label">选择公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>-->
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <!--<div class="form-group">-->
          <!--<label class="col-sm-3 control-label">使用部门</label>-->
          <!--<div class="col-sm-8">-->
            <!--<select id="using_department" style="width: 100%">-->
              <!--<option selected="selected" value="0">选择使用部门</option>-->
            <!--</select>-->
          <!--</div>-->
      <!--</div>-->
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
`

// 调换固定资产所需的table
var exchange_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>所属公司</th>
          <th>资产编号</th>
          <th>位置</th>
          <!--<th>使用部门</th>-->
          <th>保管人</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 调换列管资产所需的数据
var exchange_sub_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">原资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='raw_assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">新资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='new_assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`

// 调换列管资产所需的table
var exchange_sub_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>原资产编号</th>
          <th>类型</th>
          <th>型号</th>
          <th>新资产编号</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 回收固定资产所需的数据
var recycle_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">仓库区域</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='warehousing_region'>
                <option value="0" selected="selected">选择仓库区域</option>
            </select>
          </div>
      </div>
`

// 回收固定资产所需的table
var recycle_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>位置</th>
          <th>仓库区域</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 回收列管资产从固定资产所需的数据
var recycle_sub_assets_from_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">主机资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='raw_assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">回收配件类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">回收配件型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">回收存放位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`


// 回收列管资产从固定资产的table
var recycle_sub_assets_from_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>类型</th>
          <th>型号</th>
          <th>位置</th>
          <th>保管人</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 回收从外借回收列管资产
var recycle_sub_assets_from_checkout_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">来源公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">来源位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择来源位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">目标公司</label>
          <div class="col-sm-8">
            <select id="to_company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">目标位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='target_pos'>
                  <option value="0" selected="selected">选择目标位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`

// 回收从外借回收列管资产的table
var recycle_sub_assets_from_checkout_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>来源公司</th>
          <th>来源位置</th>
          <th>型号</th>
          <th>类型</th>
          <th>目标公司</th>
          <th>目标位置</th>
          <th>目标保管人</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 回收合并固定资产
var recycle_merge_assets_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">合并资产</label>
          <div class="col-sm-8">
            <select id="merge_assets" style="width: 100%">
              <option selected="selected" value="0">选择资产</option>
            </select>
          </div>
      </div>
`

// 回收合并固定资产所需的table
var recycle_merge_assets_table = `
      <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>合并资产</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 外借固定资产所需的数据
var checkout_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">外借公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <!--<div class="form-group">-->
          <!--<label class="col-sm-3 control-label">使用部门</label>-->
          <!--<div class="col-sm-8">-->
            <!--<select id="using_department" style="width: 100%">-->
              <!--<option selected="selected" value="0">选择使用部门</option>-->
            <!--</select>-->
          <!--</div>-->
      <!--</div>-->
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
`

// 外借固定资产所需的table
var checkout_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>公司</th>
          <th>位置</th>
          <!--<th>使用部门</th>-->
          <th>保管人</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 外借列管资产所需的数据
var checkout_sub_assets_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">来源公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">来源位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择来源位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">外借公司</label>
          <div class="col-sm-8">
            <select id="to_company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">目标位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='target_pos'>
                  <option value="0" selected="selected">选择目标位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`

// 外借列管资产所需的table
var checkout_sub_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>来源公司</th>
          <th>来源位置</th>
          <th>型号</th>
          <th>类型</th>
          <th>外借公司</th>
          <th>目标位置</th>
          <th>目标保管人</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 损毁固定资产所需的数据
var damage_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">选择要存放的库房</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">使用部门</label>
          <div class="col-sm-8">
            <select id="using_department" style="width: 100%">
              <option selected="selected" value="0">选择使用部门</option>
            </select>
          </div>
      </div>
`

// 损毁固定资产所需的table
var damage_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>位置</th>
          <th>使用部门</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 损毁列管资产所需的数据
var damage_sub_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='raw_assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`

// 损毁列管资产所需的table
var damage_sub_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>类型</th>
          <th>型号</th>
          <th>位置</th>
          <th>保管人</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 清理固定资产所需的数据
var clean_asssets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
`

// 清理固定资产的table
var clean_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 清理列管资产所需的数据
var clean_sub_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">来源位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择来源位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">目标位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='target_pos'>
                  <option value="0" selected="selected">选择目标位置</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`

// 清理列管资产的table
var clean_sub_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>来源位置</th>
          <th>型号</th>
          <th>类型</th>
          <th>目标位置</th>
          <th>目标保管人</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 位置变更所需的数据
var pos_change_modal = `
      <div class="form-group">
          <label class="col-sm-3 control-label">所属公司</label>
          <div class="col-sm-8">
            <select id="company_code" style="width: 100%">
              <option selected="selected" value="0">选择公司</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">变更人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择变更人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">变更位置</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='pos'>
                  <option value="0" selected="selected">选择目标位置</option>
              </select>
            </div>
      </div>
`

// 变更位置所需的table
var pos_change_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>所属公司</th>
          <th>变更人</th>
          <th>变更位置</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`


// 变卖固定资产所需的数据
var selloff_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">选择要存放的库房</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">使用部门</label>
          <div class="col-sm-8">
            <select id="using_department" style="width: 100%">
              <option selected="selected" value="0">选择使用部门</option>
            </select>
          </div>
      </div>
`

// 损毁固定资产所需的table
var selloff_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>位置</th>
          <th>使用部门</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`

// 损毁列管资产所需的数据
var selloff_sub_assets_modal = `
      <div class="form-group">
            <label class="col-sm-3 control-label">资产编号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='raw_assets'>
                  <option value="0" selected="selected">选择资产编号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">类型</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='ctype'>
                  <option value="0" selected="selected">选择类型</option>
                  <option value="1">主板</option>
                  <option value="2">固态硬盘</option>
                  <option value="3">机械硬盘</option>
                  <option value="4">内存</option>
                  <option value="5">显卡</option>
                  <option value="6">CPU</option>
              </select>
            </div>
      </div>
      <div class="form-group">
            <label class="col-sm-3 control-label">型号</label>
            <div class="col-sm-8">
              <select style="width: 100%" id='smodel'>
                  <option value="0" selected="selected">选择型号</option>
              </select>
            </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">位置</label>
          <div class="col-sm-8">
            <select style="width: 100%" id='pos'>
                <option value="0" selected="selected">选择位置</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">保管人</label>
          <div class="col-sm-8">
            <select id="user" style="width: 100%">
              <option selected="selected" value="0">选择保管人</option>
            </select>
          </div>
      </div>
      <div class="form-group">
          <label class="col-sm-3 control-label">数量</label>
          <div class="col-sm-8">
            <input type="text" class="form-control" id="number" value=1>
          </div>
      </div>
`

// 损毁列管资产所需的table
var selloff_sub_assets_table = `
    <table id="mytable" class="display" width="120%" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>资产编号</th>
          <th>类型</th>
          <th>型号</th>
          <th>位置</th>
          <th>保管人</th>
          <th>数量</th>
          <th>操作</th>
        </tr>
      </thead>
  </table>
`


// 初始化类别函数，电子设备，其他电子设备
function initCtype(selector) {
    selector.select2({
        minimumResultsForSearch: Infinity,
    });
}

// 通过ajax请求列管资产的类型
function initCtypeAjax(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_ctype/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 根据列管资产的类型调整modal
/*function adjust_modal(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var ctype = $("#ctype").select2('data')[0].text;
        if (assets_event == '领用' && assets_type == '列管资产'){
            if ( ctype == '手机' ){
                $("#assets").parent().parent().hide();
                $("#user").parent().parent().show();
                $("#target_pos").parent().parent().show();
            } else {
                $("#user").parent().parent().hide();
                $("#assets").parent().parent().show();
                $("#target_pos").parent().parent().hide();
            }
            
        }
    }
}*/

//初始化下拉选择公司代号
function initCompanyCode(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_company_code/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                            code: item.code,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

//初始化下拉选择部门(旧)
function initUsingDepartment(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_using_department/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

//初始化下拉选择新组织架构(新)
function initNewOrganization(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_new_organization/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

//初始化下拉选择全体用户
function initAllUser(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_all_users/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 初始化模板下拉框
function initAsstesTemplate(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_assets_template/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    }).on("select2:select", function (e) {
        auto_fill("select2:select", e);
    });
}

function auto_fill(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        var assets_template = $("#assets_template").select2('data')[0].id;
        var data = {
            'id': assets_template,
        };

        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/it_assets/get_assets_template/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                // console.log(data);
                // $("#name").val(data.name).trigger('change');
                initSelect2('name', data.name, data.name);
                $("#with_cpu").val(data.cpu);
                $("#board").val(data.board);
                $("#with_ssd").val(data.ssd);
                $("#with_disk").val(data.disk);
                $("#with_mem").val(data.mem);
                $("#with_graphics").val(data.graphics);
                $("#brand").val(data.brand);
                $("#specification").val(data.specification);
                $("#remark").val(data.remark);
                //$("#using_department").val(data.using_department);

            },
        });
    }

}


// 下拉选择固定资产名单
function initAssetsName(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_assets_name/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 下拉选择固定资产名单
function initAssetsWarehousingRegion(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_warehousing_region/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 下拉选择列管资产名单
function initShellAssetsName(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_shell_assets_name/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initSmodel(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_smodel/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    ctype: $("#ctype").select2('data')[0].text,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initAssetsSmodel(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_assets_smodel/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    assets: $("#raw_assets").select2('data')[0].id,
                    ctype: $("#ctype").select2('data')[0].text,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 展示主机里面的配件，带公司名
function initAssetsSmodelWithCompany(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_assets_smodel_with_company/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    assets: $("#raw_assets").select2('data')[0].id,
                    ctype: $("#ctype").select2('data')[0].text,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initSupplier(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_supplier/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initAssets(selector, status) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_it_assets/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    status: status,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initAssetsWithCompany(selector, status, show_user) {
    show_user = typeof show_user !== 'undefined' ? show_user : 0;
    selector.select2({
        ajax: {
            url: '/it_assets/list_it_assets/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    status: status,
                    company_code_id: $("#company_code").select2('data')[0].id,
                    show_user: show_user,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initPos(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_pos/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function initWarehousingRegion(selector) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_warehousing_region/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 下拉展示主机配件，有公司的限制
function initPartModelStatus(selector, status) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_part_model_status/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    pos: $("#pos").select2('data')[0].id,
                    company_code: $("#company_code").select2('data')[0].id,
                    ctype: $("#ctype").select2('data')[0].text,
                    status: status,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

// 下拉展示主机配件，没有公司的限制
function initPartModelStatusWithoutCompany(selector, status) {
    selector.select2({
        ajax: {
            url: '/it_assets/list_part_model_status_without_company/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    pos: $("#pos").select2('data')[0].id,
                    // company_code: $("#company_code").select2('data')[0].id,
                    ctype: $("#ctype").select2('data')[0].text,
                    status: status,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}

function resetAssetsType() {
    // 重置资产类型的下拉选项

}


// 是否新购买select2初始化
function initPurchase() {
    $("#purchase").select2({
        minimumResultsForSearch: Infinity,
    });
}


function initModalSelect2() {
    // 初始化select2

    $select2assets_event = $("#event").select2();
    $select2assets_event;
    $select2assets_event.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $select2AssetsType = $("#assets_type").select2({minimumResultsForSearch: Infinity});
    $select2AssetsType;
    $select2AssetsType.on("select2:select", function (e) {
        log2("select2:select", e);
    });


    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };

};


function log(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        assets_event = $("#event").select2('data')[0].text;
        dataTable = new Array();
        $("#mytable").remove();
        id = 1;

        if (assets_event == '回收') {
            $("#assets_type").html('');
            $("#assets_type").append('<option value="0" selected="selected">固定资产</option>');
            $("#assets_type").append('<option value="1">列管资产</option>');
            $("#assets_type").append('<option value="2">从固定资产回收主机配件</option>');
            $("#assets_type").append('<option value="3">回收合并固定资产</option>');
            // $("#assets_type").append('<option value="3">从外借回收主机配件</option>');
            $("#assets_type").val('0').trigger('change');
            assets_type = $("#assets_type").select2('data')[0].text;
        } else if (assets_event == '入库') {
            $("#assets_type").html('');
            $("#assets_type").append('<option value="0" selected="selected">固定资产</option>');
            $("#assets_type").append('<option value="1">列管资产</option>');
            $("#assets_type").append('<option value="2">主机配件</option>');
            $("#assets_type").val('0').trigger('change');
            assets_type = $("#assets_type").select2('data')[0].text;

        } else if (assets_event == '位置') {
            $("#assets_type").html('');
            $("#assets_type").append('<option value="0" selected="selected">位置变更</option>');
            $("#assets_type").val('0').trigger('change');
            assets_type = $("#assets_type").select2('data')[0].text;

        } else if (assets_event == '领用') {
            $("#assets_type").html('');
            $("#assets_type").append('<option value="0" selected="selected">固定资产</option>');
            $("#assets_type").append('<option value="1">列管资产</option>');
            $("#assets_type").append('<option value="2">主机配件</option>');
            $("#assets_type").append('<option value="3">固定资产合并</option>');
            $("#assets_type").val('0').trigger('change');
            assets_type = $("#assets_type").select2('data')[0].text;

        } else {
            $("#assets_type").html('');
            $("#assets_type").append('<option value="0" selected="selected">固定资产</option>');
            $("#assets_type").append('<option value="1">列管资产</option>');
            $("#assets_type").append('<option value="2">主机配件</option>');
            $("#assets_type").val('0').trigger('change');
            assets_type = $("#assets_type").select2('data')[0].text;
        }

    }
}

function log2(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        assets_type = $("#assets_type").select2('data')[0].text;
        dataTable = new Array();
        $("#mytable").remove();
        id = 1;
    }
}


function del(id) {
    dataTable = $.grep(dataTable, function (e) {
        return e.id != id;
    });
    reloadDataTable();
}

// 重新加载datatable的数据
function reloadDataTable() {
    table.clear().draw();
    table.rows.add(dataTable);    // add new data
    table.columns.adjust().draw(); // Redraw the DataTable
}


function checkBefore(title, content, applicant) {
    if (title == '') {
        alert('请输入标题');
        return false;
    }

    if (content == '') {
        alert('请输入内容');
        return false;
    }

    if (applicant == '0') {
        alert('请选择申请人!');
        return false;
    }

    return true;

}


function get_assets() {
    // 获取入库的资产的数据，格式
    // [
    //   {'itype': itype, 'imodel': imodel, 'assets_number': assets_number, 'price': price, 'supplier', supplier, 'belong_to': belong_to},
    //   {'itype': itype, 'imodel': imodel, 'assets_number': assets_number, 'price': price, 'supplier', supplier, 'belong_to': belong_to},
    //   {'itype': itype, 'imodel': imodel, 'assets_number': assets_number, 'price': price, 'supplier', supplier, 'belong_to': belong_to},
    // ]
    var content = new Array();
    $(".itype").each(function (i, e) {
        // itype
        var itype = $(e).val();
        if (itype == '') {
            alert('请输入类型!');
            content = false;
            return content;
        }

        // imodel
        var imodel = $(e).parent().parent().find('.imodel').val();
        if (itype == '') {
            alert('请输入型号!');
            content = false;
            return content;
        }

        // assets_number
        var assets_number = $(e).parent().parent().find('.assets_number').val();
        if (assets_number == '') {
            alert('请输入资产编号!');
            content = false;
            return content;
        } else {
            if (!/^[A-Z]{2}-\d{4}-\w{5}$/.test(assets_number)) {
                alert('资产编号格式不对');
                content = false;
                return content;
            }
        }

        // price
        var price = $(e).parent().parent().find('.price').val();
        if (price == '') {
            alert('请输入单价!');
            content = false;
            return content;
        }

        // supplier
        var supplier = $(e).parent().parent().find('.supplier').select2('data')[0].id;
        if (supplier == '0') {
            alert('请选择供应商!');
            content = false;
            return content;
        }

        // belong_to
        var belong_to = $(e).parent().parent().find('.belong_to').select2('data')[0].id;


        var item = {}
        item['itype'] = itype;
        item['imodel'] = imodel;
        item['assets_number'] = assets_number;
        item['price'] = price;
        item['supplier'] = supplier;
        item['belong_to'] = belong_to;

        content.push(item);

    });

    return content;
}


function init_table(selector) {

}


function initUser(selector) {
    // var data = ['yanwenchi', 'zhangwenhui', 'litianlai'];
    // var appendTo = selector.autocomplete( "option", "appendTo" );
    selector.autocomplete({
        source: function (request, response) {
            $.ajax({
                url: "/it_assets/list_user/",
                type: "POST",
                dataType: "json",
                data: {term: request.term},
                success: function (data) {
                    response(data);
                }
            });
        },
    });
}

$(document).ready(function () {

    // init_user();

    workflow = $("#workflow_id").text();

    initModalSelect2();

    assets_event = $("#event").select2('data')[0].text;

    assets_type = $("#assets_type").select2('data')[0].text;

    $("#show_scheme").hide();

    window.onbeforeunload = function () {
        if (dataTable.length) {
            return '你还有没提交的数据，确定离开?';
        }
    }

    // 提交
    $("#bt-commit").confirm({
        text: "确定提交?",
        confirm: function (button) {

            var inputs = {
                'assets_event': assets_event,
                'assets_type': assets_type,
                'dataTable': dataTable,
            }

            var encoded = $.toJSON(inputs);
            var pdata = encoded;

            assets_content = true;

            if (assets_content) {
                $.ajax({
                    type: "POST",
                    url: "/it_assets/do_event/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.data) {
                            $.toast({
                                text: "操作成功", // Text that is to be shown in the toast
                                heading: 'Success', // Optional heading to be shown on the toast
                                icon: 'success', // Type of toast icon
                                showHideTransition: 'slide', // fade, slide or plain
                                allowToastClose: true, // Boolean value true or false
                                hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                                stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                                position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values


                                textAlign: 'left',  // Text alignment i.e. left, right or center
                                loader: true,  // Whether to show loader or not. True by default
                                loaderBg: '#9EC600',  // Background color of the toast loader
                                beforeShow: function () {
                                }, // will be triggered before the toast is shown
                                afterShown: function () {
                                }, // will be triggered after the toat has been shown
                                beforeHide: function () {
                                }, // will be triggered before the toast gets hidden
                                afterHidden: function () {
                                    dataTable = new Array();
                                    location.reload();
                                }  // will be triggered after the toast has been hidden
                            });

                        } else {
                            alert(data.msg);
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });


    // 生成打印单
    $("#bt-create").confirm({
        text: "确定生成打印单?",
        confirm: function (button) {

            var inputs = {
                'assets_event': assets_event,
                'assets_type': assets_type,
                'dataTable': dataTable,
            };

            var encoded = $.toJSON(inputs);
            var pdata = encoded;

            assets_content = true;

            if (assets_content) {
                $.ajax({
                    type: "POST",
                    url: "/it_assets/create_application_form/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (result) {
                        var assets_id_list = result['assets_id_list'];
                        $.ajax({
                            type: "POST",
                            url: "/it_assets/assets_application_form/",
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify(assets_id_list),
                            success: function (result) {
                                var w = window.open();
                                $(w.document.body).html(result);
                            }
                        });
                    },
                    error: function (errorMsg) {

                    }

                });
            }
        },

        cancel: function (button) {

        }
        ,
        confirmButton: "确定",
        cancelButton:
            "取消",

    });


    $("#cancle-btn").click(function () {
        $(".cancel").remove();
        $("#svn_scheme").val('0').trigger('change');
    });

    $("#bt-save").click(function () {
            if (assets_event == '入库') {
                if (assets_type == '固定资产') {
                    var ctype = $("#ctype").select2('data')[0].id;
                    var ctype_text = $("#ctype").select2('data')[0].text;
                    var purchase_id = $("#purchase").select2('data')[0].id;
                    var purchase = $("#purchase").select2('data')[0].text;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var company_text = $("#company_code").select2('data')[0].text;
                    var company_code = $("#company_code").select2('data')[0].code;
                    var name = $("#name").select2('data')[0].text;
                    var with_cpu = $("#with_cpu").val();
                    var board = $("#board").val();
                    var with_ssd = $("#with_ssd").val();
                    var with_disk = $("#with_disk").val();
                    var with_mem = $("#with_mem").val();
                    var with_graphics = $("#with_graphics").val();
                    var brand = $("#brand").val();
                    var specification = $("#specification").val();
                    var using_department_id = $("#using_department").select2('data')[0].id;
                    var using_department = $("#using_department").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var supplier_id = $("#supplier").select2('data')[0].id;
                    var supplier = $("#supplier").select2('data')[0].text;
                    var number = $("#number").val();
                    var price = $("#price").val();
                    var remark = $("#remark").val();
                    var warehousing_region_id = $("#warehousing_region").select2('data')[0].id;
                    var warehousing_region = $("#warehousing_region").select2('data')[0].text;
                    console.log(warehousing_region_id)

                    if (pos_id == '0') {
                        $('#lb-msg').text('请选择位置!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (company_code_id == '0') {
                        $('#lb-msg').text('请选择公司!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (with_cpu != '') {
                        var patt = /^(\w*)-(\w*)$/;
                        if (!patt.test(with_cpu)) {
                            $('#lb-msg').text('CPU输入格式不正确，如：i5-3460');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    if (using_department_id == '0') {
                        $('#lb-msg').text('请选择使用部门!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (purchase == '是') {
                        if (supplier_id == '0') {
                            $('#lb-msg').text('请选择供应商!');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    if (name == '选择资产名称' | name == '') {
                        $('#lb-msg').text('请选择资产名称!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (purchase == '是') {
                        if (price == '') {
                            $('#lb-msg').text('请输入单价!');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    for (var i = 1; i <= number; i++) {
                        id = id + 1;
                        var data = {
                            'id': id,
                            'ctype': ctype,
                            'ctype_text': ctype_text,
                            'name': name,
                            'warehousing_region_id': warehousing_region_id,
                            'warehousing_region': warehousing_region,
                            'company_code_id': company_code_id,
                            'company_code': company_code,
                            'company_text': company_text,
                            'purchase_id': purchase_id,
                            'purchase': purchase,
                            'with_cpu': with_cpu,
                            'board': board,
                            'with_ssd': with_ssd,
                            'with_disk': with_disk,
                            'with_mem': with_mem,
                            'with_graphics': with_graphics,
                            'brand': brand,
                            'specification': specification,
                            'using_department': using_department,
                            'pos_id': pos_id,
                            'pos': pos,
                            'supplier': supplier,
                            'supplier_id': supplier_id,
                            'price': price,
                            'remark': remark,
                        };
                        dataTable.push(data);
                    }
                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        // 如果不存在，则首先初始化datatables, 然后load数据
                        // $("#table-data").after(storage_assets_table);
                        $("#data-table3").append(storage_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "ctype_text"},
                                {"data": "company_text"},
                                {"data": "purchase"},
                                {"data": "name"},
                                {"data": "warehousing_region"},
                                {"data": "with_cpu"},
                                {"data": "board"},
                                {"data": "with_ssd"},
                                {"data": "with_disk"},
                                {"data": "with_mem"},
                                {"data": "with_graphics"},
                                {"data": "brand"},
                                {"data": "specification"},
                                {"data": "using_department"},
                                {"data": "pos"},
                                {"data": "supplier"},
                                {"data": "price"},
                                {"data": "remark"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 18,
                                    width: "10%",
                                    render: function (data, type, row, meta) {
                                        if (data) {
                                            if (data.length > 8) {
                                                return data.substr(0, 7) + '......';
                                            }
                                            else {
                                                return data;
                                            }
                                        }
                                        else {
                                            return data;
                                        }

                                    }
                                },
                                {
                                    targets: 19,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else if (assets_type == '列管资产') {
                    var ctype = $("#ctype").select2('data')[0].id;
                    var ctype_text = $("#ctype").select2('data')[0].text;
                    var purchase_id = $("#purchase").select2('data')[0].id;
                    var purchase = $("#purchase").select2('data')[0].text;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var company_text = $("#company_code").select2('data')[0].text;
                    var company_code = $("#company_code").select2('data')[0].code;
                    var name = $("#name").select2('data')[0].text;
                    var brand = $("#brand").val();
                    var specification = $("#specification").val();
                    var using_department_id = $("#using_department").select2('data')[0].id;
                    var using_department = $("#using_department").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var supplier_id = $("#supplier").select2('data')[0].id;
                    var supplier = $("#supplier").select2('data')[0].text;
                    var number = $("#number").val();
                    var price = $("#price").val();
                    var remark = $("#remark").val();

                    if (pos_id == '0') {
                        $('#lb-msg').text('请选择位置!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (company_code_id == '0') {
                        $('#lb-msg').text('请选择公司!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (using_department_id == '0') {
                        $('#lb-msg').text('请选择使用部门!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (purchase == '是') {
                        if (supplier_id == '0') {
                            $('#lb-msg').text('请选择供应商!');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    if ($("#name").select2('data')[0].id == '0') {
                        $('#lb-msg').text('请选择列管资产名称!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (purchase == '是') {
                        if (price == '') {
                            $('#lb-msg').text('请输入单价!');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    for (var i = 1; i <= number; i++) {
                        id = id + 1;
                        var data = {
                            'id': id,
                            'ctype': ctype,
                            'ctype_text': ctype_text,
                            'name': name,
                            'company_code_id': company_code_id,
                            'company_code': company_code,
                            'purchase_id': purchase_id,
                            'purchase': purchase,
                            'company_text': company_text,
                            'with_cpu': with_cpu,
                            'board': board,
                            'with_ssd': with_ssd,
                            'with_disk': with_disk,
                            'with_mem': with_mem,
                            'with_graphics': with_graphics,
                            'brand': brand,
                            'specification': specification,
                            'using_department': using_department,
                            'pos_id': pos_id,
                            'pos': pos,
                            'supplier': supplier,
                            'supplier_id': supplier_id,
                            'price': price,
                            'remark': remark,
                        }
                        dataTable.push(data);
                    }

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        // 如果不存在，则首先初始化datatables, 然后load数据
                        // $("#table-data").after(storage_assets_table);
                        $("#data-table3").append(storage_shell_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_text"},
                                {"data": "ctype_text"},
                                {"data": "purchase"},
                                {"data": "name"},
                                {"data": "brand"},
                                {"data": "specification"},
                                {"data": "using_department"},
                                {"data": "pos"},
                                {"data": "supplier"},
                                {"data": "price"},
                                {"data": "remark"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 11,
                                    width: "10%",
                                    render: function (data, type, row, meta) {
                                        if (data) {
                                            if (data.length > 8) {
                                                return data.substr(0, 7) + '......';
                                            }
                                            else {
                                                return data;
                                            }
                                        }
                                        else {
                                            return data;
                                        }

                                    }
                                },
                                {
                                    targets: 12,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }

                }
                else {   // 入库主机配件
                    id = id + 1;
                    var sub_assets_type = $("#sub_assets_type").select2('data')[0].text;
                    var purchase_id = $("#purchase").select2('data')[0].id;
                    var purchase = $("#purchase").select2('data')[0].text;
                    var brand = $("#brand").val();
                    var smodel = $("#smodel").val();
                    var number = $("#number").val();
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var supplier_id = $("#supplier").select2('data')[0].id;
                    var supplier = $("#supplier").select2('data')[0].text;
                    var company_id = $("#company").select2('data')[0].id;
                    var company_name = $("#company").select2('data')[0].text;
                    var price = $("#price").val();

                    if (purchase == '是') {
                        if (supplier_id == '0') {
                            $('#lb-msg').text('请选择供应商!');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    if (company_id == '0') {
                        $('#lb-msg').text('请选择公司!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (sub_assets_type == '请选择资产类型') {
                        $('#lb-msg').text('请选择资产类型!');
                        $('#modal-notify').show();
                        return false;
                    }


                    // if (using_department_id == '0') {
                    //     $('#lb-msg').text('请选择使用部门!');
                    //     $('#modal-notify').show();
                    //     return false;
                    // }

                    if (purchase == '是') {
                        if (price == '') {
                            $('#lb-msg').text('请输入单价!');
                            $('#modal-notify').show();
                            return false;
                        }
                    }

                    var data = {
                        'id': id,
                        'company_id': company_id,
                        'company_name': company_name,
                        'purchase_id': purchase_id,
                        'purchase': purchase,
                        'sub_assets_type': sub_assets_type,
                        'smodel': smodel,
                        'number': number,
                        'pos_id': pos_id,
                        'pos': pos,
                        'supplier_id': supplier_id,
                        'supplier': supplier,
                        'price': price,
                        'brand': brand,
                    };
                    dataTable.push(data);
                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(storage_sub_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_name"},
                                {"data": "purchase"},
                                {"data": "sub_assets_type"},
                                {"data": "brand"},
                                {"data": "smodel"},
                                {"data": "number"},
                                {"data": "pos"},
                                {"data": "supplier"},
                                {"data": "price"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 10,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                }
            } else if (assets_event == '领用') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    //var using_department_id = $("#using_department").select2('data')[0].id;
                    //var using_department = $("#using_department").select2('data')[0].text;
                    var user = $("#user").select2('data')[0].text;
                    // var company_code_id = $("#company_code").select2('data')[0].id;
                    // var company_code = $("#company_code").select2('data')[0].text;

                    // if (using_department_id == '0') {
                    //     $('#lb-msg').text('请选择使用部门!');
                    //     $('#modal-notify').show();
                    //     return false;
                    // }

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                        'pos_id': pos_id,
                        'pos': pos,
                        //'using_department': using_department,
                        'user': user,
                        // 'company_code': company_code,
                        // 'company_code_id': company_code_id,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(receive_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                // {"data": "company_code"},
                                {"data": "assets_number"},
                                {"data": "pos"},
                                //{"data": "using_department"},
                                {"data": "user"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 4,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else if (assets_type == '固定资产合并') {
                    id = id + 1;
                    var merge_assets = $("#merge_assets").select2('data')[0].text;
                    var assets = $("#assets").select2('data')[0].text;

                    var merge_assets_id = $("#merge_assets").val();
                    var assets_id = $("#assets").val();

                    if (merge_assets_id == '0' | assets_id == '0') {
                        $('#lb-msg').text('请选择资产编号!');
                        $('#modal-notify').show();
                        return false;
                    }

                    var data = {
                        'id': id,
                        'merge_assets': merge_assets,
                        'assets': assets,
                        'merge_assets_id': merge_assets_id,
                        'assets_id': assets_id,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(receive_assets_merge_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets"},
                                {"data": "merge_assets"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 3,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }

                } else {
                    id = id + 1;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var pos = $("#pos").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var part_model_status = $("#smodel").select2('data')[0].id;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var company_code = $("#company_code").select2('data')[0].text;

                    var assets = $("#assets").select2('data')[0].id;
                    if (assets == '0') {
                        var assets_number = '';
                    } else {
                        var assets_number = $("#assets").select2('data')[0].text;
                    }

                    if (company_code_id == '0') {
                        $('#lb-msg').text('请选择公司!');
                        $('#modal-notify').show();
                        return false;
                    }

                    var number = $("#number").val();

                    var data = {
                        'id': id,
                        'company_code': company_code,
                        'company_code_id': company_code_id,
                        'ctype': ctype,
                        'smodel': smodel,
                        'pos': pos,
                        'pos_id': pos_id,
                        'part_model_status': part_model_status,
                        'assets': assets,
                        'assets_number': assets_number,
                        'number': number,
                    };

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(receive_sub_asssets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_code"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "pos"},
                                {"data": "assets_number"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 7,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }
                }
            } else if (assets_event == '调拨') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    //var using_department_id = $("#using_department").select2('data')[0].id;
                    //var using_department = $("#using_department").select2('data')[0].text;
                    var user = $("#user").select2('data')[0].text;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var company_code = $("#company_code").select2('data')[0].text;

                    if (company_code_id == '0') {
                        $('#lb-msg').text('请选择公司!');
                        $('#modal-notify').show();
                        return false;
                    }

                    // if (using_department_id == '0') {
                    //     $('#lb-msg').text('请选择使用部门!');
                    //     $('#modal-notify').show();
                    //     return false;
                    // }

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                        'pos_id': pos_id,
                        'pos': pos,
                        //'using_department': using_department,
                        'user': user,
                        'company_code_id': company_code_id,
                        'company_code': company_code,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(exchange_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_code"},
                                {"data": "assets_number"},
                                {"data": "pos"},
                                //{"data": "using_department"},
                                {"data": "user"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 5,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else {
                    id += 1;
                    var raw_assets = $("#raw_assets").select2('data')[0].id;
                    var raw_assets_number = $("#raw_assets").select2('data')[0].text;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var raw_assets_part_model = $("#smodel").select2('data')[0].id;
                    var new_assets = $("#new_assets").select2('data')[0].id;
                    var new_assets_number = $("#raw_assets").select2('data')[0].text;
                    var number = $("#number").val();

                    data = {
                        'id': id,
                        'raw_assets': raw_assets,
                        'raw_assets_number': raw_assets_number,
                        'ctype': ctype,
                        'smodel': smodel,
                        'raw_assets_part_model': raw_assets_part_model,
                        'new_assets': new_assets,
                        'new_assets_number': new_assets_number,
                        'number': number,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(exchange_sub_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "raw_assets_number"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "new_assets_number"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 6,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                }
            } else if (assets_event == '回收') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var warehousing_region = $("#warehousing_region").select2('data')[0].text;
                    var warehousing_region_id = $("#warehousing_region").select2('data')[0].id;

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                        'pos_id': pos_id,
                        'pos': pos,
                        'warehousing_region_id': warehousing_region_id,
                        'warehousing_region': warehousing_region,

                    };

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(recycle_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {"data": "pos"},
                                {"data": "warehousing_region"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 4,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else if (assets_type == '从固定资产回收主机配件') {
                    id += 1;
                    var raw_assets = $("#raw_assets").select2('data')[0].id;
                    var assets_number = $("#raw_assets").select2('data')[0].text;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var raw_assets_part_model = $("#smodel").select2('data')[0].id;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var user = $("#user").select2('data')[0].text;
                    var number = $("#number").val();

                    data = {
                        'id': id,
                        'raw_assets': raw_assets,
                        'assets_number': assets_number,
                        'ctype': ctype,
                        'smodel': smodel,
                        'raw_assets_part_model': raw_assets_part_model,
                        'pos_id': pos_id,
                        'pos': pos,
                        'user': user,
                        'number': number,
                    }

                    // 遍历之前添加数据
                    // 如果smodel已经添加，则不能继续添加
                    for (d in dataTable) {
                        if (raw_assets_part_model == dataTable[d].raw_assets_part_model) {
                            alert('已经添加该项!')
                            return false
                        }
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(recycle_sub_assets_from_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "pos"},
                                {"data": "user"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 7,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }

                } else if (assets_type == '回收合并固定资产') {
                    id = id + 1;
                    var merge_assets = $("#merge_assets").select2('data')[0].text;
                    var merge_assets_id = $("#merge_assets").val();

                    var data = {
                        'id': id,
                        'merge_assets': merge_assets,
                        'merge_assets_id': merge_assets_id,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(recycle_merge_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "merge_assets"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 2,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }

                } else if (assets_type == '从外借回收主机配件') {
                    id = id + 1;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var pos = $("#pos").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var target_pos_id = $("#target_pos").select2('data')[0].id;
                    var target_pos = $("#target_pos").select2('data')[0].text;
                    var part_model_status = $("#smodel").select2('data')[0].id;
                    var number = $("#number").val();
                    var user = $("#user").select2('data')[0].text;
                    var company_code = $("#company_code").select2('data')[0].text;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var to_company_code = $("#to_company_code").select2('data')[0].text;
                    var to_company_code_id = $("#to_company_code").select2('data')[0].id;

                    var data = {
                        'id': id,
                        'ctype': ctype,
                        'smodel': smodel,
                        'pos': pos,
                        'pos_id': pos_id,
                        'target_pos': target_pos,
                        'target_pos_id': target_pos_id,
                        'part_model_status': part_model_status,
                        'number': number,
                        'user': user,
                        'company_code': company_code,
                        'company_code_id': company_code_id,
                        'to_company_code': to_company_code,
                        'to_company_code_id': to_company_code_id,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(recycle_sub_assets_from_checkout_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_code"},
                                {"data": "pos"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "to_company_code"},
                                {"data": "target_pos"},
                                {"data": "user"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 9,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }

                }
            } else if (assets_event == '外借') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var using_department_id = $("#using_department").select2('data')[0].id;
                    var using_department = $("#using_department").select2('data')[0].text;
                    var user = $("#user").select2('data')[0].text;

                    var company_code_id = $('#company_code').select2('data')[0].id;
                    var company_code = $('#company_code').select2('data')[0].text;

                    if (using_department_id == '0') {
                        $('#lb-msg').text('请选择使用部门!');
                        $('#modal-notify').show();
                        return false;
                    }

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                        'pos_id': pos_id,
                        'pos': pos,
                        'using_department': using_department,
                        'user': user,
                        'company_code': company_code,
                        'company_code_id': company_code_id,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(checkout_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_code"},
                                {"data": "assets_number"},
                                {"data": "pos"},
                                {"data": "using_department"},
                                {"data": "user"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 6,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else {
                    id = id + 1;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var pos = $("#pos").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var target_pos_id = $("#target_pos").select2('data')[0].id;
                    var target_pos = $("#target_pos").select2('data')[0].text;
                    var part_model_status = $("#smodel").select2('data')[0].id;
                    var number = $("#number").val();
                    var user = $("#user").select2('data')[0].text;
                    var to_company_code_id = $("#to_company_code").select2('data')[0].id;
                    var to_company_code = $("#to_company_code").select2('data')[0].text;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var company_code = $("#company_code").select2('data')[0].text;

                    var data = {
                        'id': id,
                        'ctype': ctype,
                        'smodel': smodel,
                        'pos': pos,
                        'pos_id': pos_id,
                        'target_pos': target_pos,
                        'target_pos_id': target_pos_id,
                        'part_model_status': part_model_status,
                        'number': number,
                        'user': user,
                        'company_code': company_code,
                        'company_code_id': company_code_id,
                        'to_company_code': to_company_code,
                        'to_company_code_id': to_company_code_id,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(checkout_sub_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_code"},
                                {"data": "pos"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "to_company_code"},
                                {"data": "target_pos"},
                                {"data": "user"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 9,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }
                }
            } else if (assets_event == '损毁') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var using_department_id = $("#using_department").select2('data')[0].id;
                    var using_department = $("#using_department").select2('data')[0].text;

                    if (using_department_id == '0') {
                        $('#lb-msg').text('请选择使用部门!');
                        $('#modal-notify').show();
                        return false;
                    }

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                        'pos_id': pos_id,
                        'pos': pos,
                        'using_department': using_department,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(damage_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {"data": "pos"},
                                {"data": "using_department"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 4,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else {
                    id += 1;
                    var raw_assets = $("#raw_assets").select2('data')[0].id;
                    var assets_number = $("#raw_assets").select2('data')[0].text;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var raw_assets_part_model = $("#smodel").select2('data')[0].id;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var user = $("#user").select2('data')[0].text;
                    var number = $("#number").val();

                    data = {
                        'id': id,
                        'raw_assets': raw_assets,
                        'assets_number': assets_number,
                        'ctype': ctype,
                        'smodel': smodel,
                        'raw_assets_part_model': raw_assets_part_model,
                        'pos_id': pos_id,
                        'pos': pos,
                        'user': user,
                        'number': number,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(damage_sub_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "pos"},
                                {"data": "user"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 7,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }
                }
            } else if (assets_event == '清理') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(clean_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 2,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else {
                    id = id + 1;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var pos = $("#pos").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var target_pos_id = $("#target_pos").select2('data')[0].id;
                    var target_pos = $("#target_pos").select2('data')[0].text;
                    var part_model_status = $("#smodel").select2('data')[0].id;
                    var number = $("#number").val();
                    var user = $("#user").select2('data')[0].text;

                    var data = {
                        'id': id,
                        'ctype': ctype,
                        'smodel': smodel,
                        'pos': pos,
                        'pos_id': pos_id,
                        'target_pos': target_pos,
                        'target_pos_id': target_pos_id,
                        'part_model_status': part_model_status,
                        'number': number,
                        'user': user,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(clean_sub_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "pos"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "target_pos"},
                                {"data": "user"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 7,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }
                }
            } else if (assets_event == '位置') {
                if (assets_type == '位置变更') {
                    id += 1;
                    var company_code_id = $("#company_code").select2('data')[0].id;
                    var company_code = $("#company_code").select2('data')[0].text;

                    var user = $("#user").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;

                    if (company_code_id == '0') {
                        $('#lb-msg').text('请选择公司!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (pos_id == '0') {
                        $('#lb-msg').text('请选择变更位置!');
                        $('#modal-notify').show();
                        return false;
                    }

                    if (user == '') {
                        $('#lb-msg').text('请输入用户');
                        $('#modal-notify').show();
                        return false;
                    }

                    data = {
                        'id': id,
                        'company_code_id': company_code_id,
                        'company_code': company_code,
                        'pos_id': pos_id,
                        'pos': pos,
                        'user': user,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(pos_change_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "company_code"},
                                {"data": "user"},
                                {"data": "pos"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 4,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                }
            } else if (assets_event == '变卖') {
                if (assets_type == '固定资产' | assets_type == '列管资产') {
                    id += 1;
                    var assets = $("#assets").select2('data')[0].id;
                    var assets_number = $("#assets").select2('data')[0].text;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var using_department_id = $("#using_department").select2('data')[0].id;
                    var using_department = $("#using_department").select2('data')[0].text;

                    if (using_department_id == '0') {
                        $('#lb-msg').text('请选择使用部门!');
                        $('#modal-notify').show();
                        return false;
                    }

                    data = {
                        'id': id,
                        'assets': assets,
                        'assets_number': assets_number,
                        'pos_id': pos_id,
                        'pos': pos,
                        'using_department': using_department,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(selloff_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {"data": "pos"},
                                {"data": "using_department"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 4,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        })
                    }
                } else {
                    id += 1;
                    var raw_assets = $("#raw_assets").select2('data')[0].id;
                    var assets_number = $("#raw_assets").select2('data')[0].text;
                    var ctype = $("#ctype").select2('data')[0].text;
                    var smodel = $("#smodel").select2('data')[0].text;
                    var raw_assets_part_model = $("#smodel").select2('data')[0].id;
                    var pos_id = $("#pos").select2('data')[0].id;
                    var pos = $("#pos").select2('data')[0].text;
                    var user = $("#user").select2('data')[0].text;
                    var number = $("#number").val();

                    data = {
                        'id': id,
                        'raw_assets': raw_assets,
                        'assets_number': assets_number,
                        'ctype': ctype,
                        'smodel': smodel,
                        'raw_assets_part_model': raw_assets_part_model,
                        'pos_id': pos_id,
                        'pos': pos,
                        'user': user,
                        'number': number,
                    }

                    dataTable.push(data);

                    if ($("#mytable").length) {
                        // 如果存在，则重新load数据
                        reloadDataTable();
                    } else {
                        $("#data-table3").append(selloff_sub_assets_table);
                        table = $("#mytable").DataTable({
                            "data": dataTable,
                            "ordering": false,
                            "paging": false,
                            "info": false,
                            "searching": false,
                            "columns": [
                                // {"data": null},
                                {"data": "id"},
                                {"data": "assets_number"},
                                {"data": "ctype"},
                                {"data": "smodel"},
                                {"data": "pos"},
                                {"data": "user"},
                                {"data": "number"},
                                {
                                    "data": null,
                                    "orderable": false,
                                }
                            ],
                            "columnDefs": [
                                {
                                    'targets': 0,
                                    'visible': false,
                                    'searchable': false
                                },
                                {
                                    targets: 7,
                                    render: function (a, b, c, d) {
                                        var context =
                                            {
                                                func: [
                                                    {"name": "删除", "fn": "del(\'" + c.id + "\')", "type": "danger"},
                                                ]
                                            };
                                        var html = template(context);
                                        return html;
                                    }
                                },
                            ],
                            "language": {
                                "url": "/static/js/i18n/Chinese.json"
                            },
                        });
                    }
                }
            }

        }
    );

    $("#myAdd").click(function () {

        if (assets_event == '入库') {
            if (assets_type == '固定资产') {
                $("#modal-data").html('');
                $("#modal-data").append(storage_assets_modal);
                $("#myModalLabel").text("入库-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");

                initAsstesTemplate($("#assets_template"));

                initCompanyCode($("#company_code"));

                initNewOrganization($("#using_department"));

                initPurchase();

                initAssetsName($("#name"));

                initAssetsWarehousingRegion($('#warehousing_region'));

                initSupplier($("#supplier"));

                initCtype($("#ctype"));

                initPos($("#pos"));

                initAllUser($("#user"));

            } else if (assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(storage_shell_assets_modal);
                $("#myModalLabel").text("入库-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");

                initCompanyCode($("#company_code"));
                initShellAssetsName($("#name"));
                initCtype($("#ctype"));
                initPurchase();
                initSupplier($("#supplier"));
                initPos($("#pos"));
                initNewOrganization($("#using_department"));
                initAllUser($("#user"));

            } else {
                // console.log('ok');
                $("#modal-data").html('');
                $("#modal-data").append(storage_sub_assets_modal);
                $("#myModalLabel").text("入库-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");

                initCtype($("#sub_assets_type"));

                initPurchase();

                initSupplier($("#supplier"));

                initPos($("#pos"));

                initCompanyCode($("#company"))

                //initNewOrganization($("#using_department"));

                initAllUser($("#user"));
            }

            $(".belong_to").select2();
        } else if (assets_event == '领用') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(exchange_assets_modal);
                $("#myModalLabel").text("领用-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initUser($("#user"));
                // initCompanyCode( $("#company_code") );
                // initAssetsWithCompany( $("#assets"), '0', show_user=1);
                initAssets($("#assets"), '0');
                initPos($("#pos"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else if (assets_type == '固定资产合并') {
                $("#modal-data").html('');
                $("#modal-data").append(receive_assets_merge_modal);
                $("#myModalLabel").text("领用-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#assets"), '1');
                initAssets($("#merge_assets"), '0');
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else {
                $("#modal-data").html('');
                $("#modal-data").append(receive_sub_asssets_modal);
                $("#myModalLabel").text("领用-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");

                initCompanyCode($("#company_code"));
                initCtypeAjax($("#ctype"));
                initPartModelStatus($("#smodel"), '0');
                // initPartModelStatusWithoutCompany( $("#smodel"), '0' );
                // initAssetsWithCompany( $("#assets"), 1);
                initAssets($("#assets"), '0,1');
                initPos($("#pos"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '调拨') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(receive_assets_modal);
                $("#myModalLabel").text("调拨-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initCompanyCode($("#company_code"));
                initAssetsWithCompany($("#assets"), '1');
                initPos($("#pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else {
                $("#modal-data").html('');
                $("#modal-data").append(exchange_sub_assets_modal);
                $("#myModalLabel").text("调拨-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#raw_assets"), 1);
                initAssets($("#new_assets"), 1);
                initCtype($("#ctype"));
                initAssetsSmodel($("#smodel"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '回收') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(recycle_assets_modal);
                $("#myModalLabel").text("回收-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#assets"), '1,2');
                initPos($("#pos"));
                initWarehousingRegion($('#warehousing_region'));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else if (assets_type == '从固定资产回收主机配件') {
                $("#modal-data").html('');
                $("#modal-data").append(recycle_sub_assets_from_assets_modal);
                $("#myModalLabel").text("回收-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#raw_assets"), '0,1,2,3,4,5,6');
                initCtype($("#ctype"));
                // initAssetsSmodel( $("#smodel") );
                initAssetsSmodelWithCompany($("#smodel"));
                initPos($("#pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else if (assets_type == '回收合并固定资产') {
                $("#modal-data").html('');
                $("#modal-data").append(recycle_merge_assets_modal);
                $("#myModalLabel").text("回收-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#merge_assets"), '1');
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else if (assets_type == '从外借回收主机配件') {
                $("#modal-data").html('');
                $("#modal-data").append(recycle_sub_assets_from_checkout_modal);
                $("#myModalLabel").text("回收-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initCompanyCode($("#company_code"));
                initCtype($("#ctype"));
                initPartModelStatus($("#smodel"), '2');
                initCompanyCode($("#to_company_code"));
                initPos($("#pos"));
                initPos($("#target_pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '外借') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(checkout_assets_modal);
                $("#myModalLabel").text("外借-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#assets"), '0,1');
                initCompanyCode($("#company_code"));
                initPos($("#pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else {
                $("#modal-data").html('');
                $("#modal-data").append(checkout_sub_assets_modal);
                $("#myModalLabel").text("外借-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initCompanyCode($("#to_company_code"));
                initCtype($("#ctype"));
                initPartModelStatus($("#smodel"), '0');
                initCompanyCode($("#company_code"));
                initPos($("#pos"));
                initPos($("#target_pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '损毁') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(damage_assets_modal);
                $("#myModalLabel").text("损毁-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#assets"), '1');
                initPos($("#pos"));
                initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else {
                $("#modal-data").html('');
                $("#modal-data").append(damage_sub_assets_modal);
                $("#myModalLabel").text("损毁-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#raw_assets"), '1');
                initCtype($("#ctype"));
                initAssetsSmodel($("#smodel"));
                initPos($("#pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '清理') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(clean_asssets_modal);
                $("#myModalLabel").text("清理-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#assets"), '4');
                initPos($("#pos"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else {
                $("#modal-data").html('');
                $("#modal-data").append(clean_sub_assets_modal);
                $("#myModalLabel").text("清理-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initCtype($("#ctype"));
                initPartModelStatus($("#smodel"), '4');
                initPos($("#pos"));
                initPos($("#target_pos"));
                initUser($("#user"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '位置') {
            if (assets_type == '位置变更') {
                $("#modal-data").html('');
                $("#modal-data").append(pos_change_modal);
                $("#myModalLabel").text("位置-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initCompanyCode($("#company_code"));
                //initUser($("#user"));
                initPos($("#pos"));
                //initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            }
        } else if (assets_event == '变卖') {
            if (assets_type == '固定资产' | assets_type == '列管资产') {
                $("#modal-data").html('');
                $("#modal-data").append(selloff_assets_modal);
                $("#myModalLabel").text("变卖-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#assets"), '0,1');
                initPos($("#pos"));
                initNewOrganization($("#using_department"));
                initAllUser($("#user"));
            } else {
                $("#modal-data").html('');
                $("#modal-data").append(selloff_sub_assets_modal);
                $("#myModalLabel").text("损毁-" + assets_type);
                $("#modal-notify").hide();
                $("#myModal").modal("show");
                initAssets($("#raw_assets"), '0,1');
                initCtype($("#ctype"));
                initAssetsSmodel($("#smodel"));
                initPos($("#pos"));
                initUser($("#user"));
                initAllUser($("#user"));
            }
        }


    });

})
;
