create table "APP_KEEPALIVE"
(
	"id" VARCHAR2(200) not null ,
	"app_name" VARCHAR2(255),
	"app_code" VARCHAR2(255),
	"app_desc" VARCHAR2(500),
	"app_url" VARCHAR2(255),
	"app_ip" VARCHAR2(255),
	"app_port" VARCHAR2(255),
	"app_state" VARCHAR2(255),
	"connect_time" VARCHAR2(255),
	"message" TEXT,
	primary key("id")
)
storage(initial 1, next 1, minextents 1, fillfactor 0)
;

comment on table "APP_KEEPALIVE" is '心跳检测日志表';

comment on column "APP_KEEPALIVE"."id" is '主键';

comment on column "APP_KEEPALIVE"."app_name" is '应用名称';

comment on column "APP_KEEPALIVE"."app_code" is '应用编目';

comment on column "APP_KEEPALIVE"."app_desc" is '应用描述';

comment on column "APP_KEEPALIVE"."app_url" is '应用测试连接地址';

comment on column "APP_KEEPALIVE"."app_ip" is '应用地址';

comment on column "APP_KEEPALIVE"."app_port" is '应用端口';

comment on column "APP_KEEPALIVE"."app_state" is '检测状态';

comment on column "APP_KEEPALIVE"."connect_time" is '检测时间';

comment on column "APP_KEEPALIVE"."message" is '异常日志';