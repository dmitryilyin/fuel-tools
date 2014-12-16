require 'rubygems'
require 'puppet/application'
require 'puppet/configurer'

# put to lib/puppet/application/res.rb of Puppet

class Puppet::Application::Res < Puppet::Application
  option("--debug","-d")
  option("--verbose","-v")

  def help
    <<-'HELP'
      Print compiled catalog
    HELP
  end

  def main
    # Set our code or file to use.
    if options[:code] or command_line.args.length == 0
      Puppet[:code] = options[:code] || STDIN.read
    else
      manifest = command_line.args.shift
      raise "Could not find file #{manifest}" unless Puppet::FileSystem::File.exist?(manifest)
      Puppet.warning("Only one file can be applied per run.  Skipping #{command_line.args.join(', ')}") if command_line.args.size > 0
      Puppet[:manifest] = manifest
    end

    unless Puppet[:node_name_fact].empty?
      # Collect our facts.
      unless facts = Puppet::Node::Facts.indirection.find(Puppet[:node_name_value])
        raise "Could not find facts for #{Puppet[:node_name_value]}"
      end

      Puppet[:node_name_value] = facts.values[Puppet[:node_name_fact]]
      facts.name = Puppet[:node_name_value]
    end

    # Find our Node
    unless node = Puppet::Node.indirection.find(Puppet[:node_name_value])
      raise "Could not find node #{Puppet[:node_name_value]}"
    end

    # Merge in the facts.
    node.merge(facts.values) if facts

    # Allow users to load the classes that puppet agent creates.
    if options[:loadclasses]
      file = Puppet[:classfile]
      if Puppet::FileSystem::File.exist?(file)
        unless FileTest.readable?(file)
          $stderr.puts "#{file} is not readable"
          exit(63)
        end
        node.classes = ::File.read(file).split(/[\s\n]+/)
      end
    end

    begin
      # Compile our catalog
      starttime = Time.now
      catalog = Puppet::Resource::Catalog.indirection.find(node.name, :use_node => node)

      # Translate it to a RAL catalog
      catalog = catalog.to_ral

      catalog.finalize

      catalog.retrieval_duration = Time.now - starttime

      def show_value(value)
        value = Array value
        out = ''
        out += '[' if value.length > 1

        value = value.map do |v|
          if v.is_a? Puppet::Resource
            class << v
              def to_s
                t = @title.gsub(%q|'|, %q|"|)
                "#{@type}['#{t}']"
              end
            end
            v.to_s
          else
            %q|'| + v.to_s.gsub(%q|'|, %q|"|) + %q|'|
          end
        end
        out += value.join ', '
        out += ']' if value.length > 1
        out
      end

      def show_name(name)
        name = name.to_s
        name.gsub!(%q|'|, %q|"|)
        name
      end

      def resource_title(resource)
        type = resource.type.to_s
        name = resource[resource.name_var]
        name.gsub!(%q|'|, %q|"|)
        "#{type} { '#{name}' :"
      end

      def print_resources(catalog)
       catalog.resources.each do |resource|
         next unless resource.managed?
         puts resource_title resource
           params = {}
           resource.parameters_with_value.each do |p|
             name = p.name
             value = p.value

             known_meta = %(alias audit before noop notify require schedule stage subscribe tag)
             unless known_meta.include? name.to_s
               next if p.metaparam?
               parameter_class_name = p.class.to_s.split('::').last
               next if parameter_class_name.start_with? 'Parameter'
             end

             if name == :content
               class << p.class
                 def actual_content
                   @actual_content
                 end
               end
               value = p.actual_content.to_s.gsub(%q|'|, %q|"|).gsub("\n", '\n')
             end

             params[show_name name] = show_value value
           end
           max_name_length = params.keys.inject(0) { |ml,p| p.length > ml ? p.length : ml }
           params.each do |k,v|
             k = k.ljust max_name_length, ' '
             puts "  #{k} => #{v},"
           end
         puts '}'
         puts
       end
      end

      print_resources catalog
      exit 0
    rescue => detail
      Puppet.log_exception(detail)
      exit(1)
    end

  end

end

version = ">= 0"

if ARGV.first
  str = ARGV.first
  str = str.dup.force_encoding("BINARY") if str.respond_to? :force_encoding
  if str =~ /\A_(.*)_\z/
    version = $1
    ARGV.shift
  end
end

gem 'puppet', version
load Gem.bin_path('puppet', 'puppet', version)

