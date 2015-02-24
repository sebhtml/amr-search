#!/usr/bin/env perl

use strict;
use vars qw($DRY_RUN) ;
use warnings;
no warnings('once');

use JSON;
use Config::Simple;
use Getopt::Long;
use LWP::UserAgent;
use MIME::Base64;
use Data::Dumper;

# Author: Andreas Wilke

$DRY_RUN = 1;

my $ua = LWP::UserAgent->new('HMP Download');
my $json = new JSON ;

my $base = 'http://api.metagenomics.anl.gov';
my $project = "mgp385";
my $verbose = 1;


print "Retrieving project from ".$base."/project/".$project."?verbosity=full\n" if ($verbose);

# Project URL
my $get = $ua->get($base."/project/".$project."?verbosity=full");

# check response status
unless ( $get->is_success ) {
print STDERR join "\t", "ERROR:", $get->code, $get->status_line;
    exit 1;
}


# decode response
my $res = $json->decode( $get->content );
my $mglist = $res->{metagenomes} ;

my $size = scalar @$mglist;

print "Project $project has $size metagenomes.";

# print STDERR $mglist, "\n";

# print Dumper $res ;

print "Searching for upload file\n" if ($verbose) ;

foreach my $tuple ( @$mglist ) {
  # url for all genome features
  my $mg = $tuple->[0] ;
  print "Checking download url ". $base."/download/$mg\n";
  my $get = $ua->get($base."/download/$mg");
  # check response status
  unless ( $get->is_success ) {
    print STDERR join "\t", "ERROR:", $get->code, $get->status_line;
    exit 1;
  }
  my $res = $json->decode( $get->content );
  my $download = undef ;
  my $dstage   = undef ;
  foreach my $stage ( @{$res->{data} } ) {
    if ($stage->{stage_name} eq "upload"){
      $download = $stage->{url};
      $dstage   = $stage;
      print join "\t" , $dstage->{stage_name} , $dstage->{file_name} , $dstage->{file_format} , $dstage->{url} , "\n"  if(defined $dstage);
    }
  }
  if(defined $dstage){
    if( $dstage->{file_format} eq "fastq" ){
      # fastq
      #my $call = "curl $download | fastq2fasta > " . $dstage->{file_name} ;
      my $call = "curl $download > " . $dstage->{file_name} ;
      my $error = system $call unless $DRY_RUN ;
    }
    elsif( $dstage->{file_format} eq "fasta"){
      # fasta
      my $call = "curl $download > " . $dstage->{file_name} ;
      my $error = system $call unless $DRY_RUN ;
    }
    else{
      # PROBLEM
      print STDERR "Not a valid sequence type for $download\n" ;
    }
  }
  else{
    print STDERR "No upload stage for $mg\n" ;
  }
}


