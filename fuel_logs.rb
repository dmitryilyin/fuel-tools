#!/usr/bin/env ruby
ASTUTE_LOG = '/tmp/astute.log'

def read_astute_log
  raise 'No Astute log!' unless File.exists? ASTUTE_LOG
  File.open(ASTUTE_LOG, 'r') do |log|
    record = ''
    log.each do |line|
      if line =~ /^(\d+-\d+-\S+\s)/
        yield record
        record = line
      else
        record += line
      end
    end
  end
end

def task_status(record)
  if record =~ /^(\S+)\s+.*?Task.*?"puppet_manifest"=>"(\S+)".*?on node uid=(\d+)\s+(.*)/
    date = $1
    manifest = $2
    uid = $3
    status = $4
    return if status == 'deploying'
    puts "#{date}: TASK END: UID: #{uid} #{manifest} #{status}"
  end
end

def task_run(record)
  if record =~ /^(\S+)\s+.*?run task.*?puppet_manifest: "(\S+)"/m
    date = $1
    manifest = $2
    uids = record.scan(/- '(\d+)'/m).map { |uid| uid.first }.join ', '
    puts "#{date}: TASK RUN: UID: #{uids} #{manifest}"
  end
end

def hook_run(record)
  if record =~ /^(\S+)\s+.*?Run hook.*?parameters:(.*)/m
    date = $1
    parameters = $2
    uids = record.scan(/- '(\d+)'/m).map { |uid| uid.first }.join ', '
    puts "#{date}: HOOK RUN: UID: #{uids} #{parameters}"
  end
end

def rpc_cast(record)
  if record =~ /^(\S+)\s+.*?Casting message to Nailgun: (.*)/m
    date = $1
    nodes = $2
    return if nodes.include? 'deploying'
    return if nodes.include? 'provisioning'
    puts "#{date}: RPC CAST: #{nodes}"
  end
end

# 2015-02-17T14:54:20 info: [409] Casting message to Nailgun: {"method"=>"deploy_resp", "args"=>{"task_uuid"=>"648d3db3-d884-4343-b24b-45759e1c0fbb", "nodes"=>[{"uid"=>"1", "status"=>"deploying", "role"=>"primary-controller", "progress"=>0}]}}

def rpc_call(record)
  if record =~/^(\S+)\s+.*?Processing RPC call\s+(.*)/
    puts "#{$1}: RPC CALL: #{$2}"
  end
end

read_astute_log do |record|
  task_status record
  task_run record
  rpc_call record
  rpc_cast record
  hook_run record
end



# while (line = log.gets)
#   if line =~ /^(\S+)\s+.*?Task.*?"puppet_manifest"=>"(\S+)".*?on node uid=(\d+)\s+(.*)/
#     date = $1
#     manifest = $2
#     uid = $3
#     status = $4
#     next if status == 'deploying'
#     puts "#{date}: UID: #{uid} Task: #{manifest} #{status}"
#   end
#   if line =~/^(\S+)\s+.*?Processing RPC call\s+(.*)/
#     puts "#{$1}: CALL: #{$2}"
#   end
# end
